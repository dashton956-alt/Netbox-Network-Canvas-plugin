from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.utils import timezone

from netbox.views import generic
from dcim.models import Device, Cable, Interface
from ipam.models import VLAN, Prefix
from . import filtersets, forms, models, tables


class NetworkCanvasView(generic.ObjectView):
    queryset = models.NetworkTopologyCanvas.objects.all()


class NetworkCanvasListView(generic.ObjectListView):
    queryset = models.NetworkTopologyCanvas.objects.all()
    table = tables.NetworkCanvasTable
    filterset = filtersets.NetworkCanvasFilterSet
    filterset_form = forms.NetworkCanvasFilterForm


class NetworkCanvasEditView(generic.ObjectEditView):
    queryset = models.NetworkTopologyCanvas.objects.all()
    form = forms.NetworkCanvasForm


class NetworkCanvasDeleteView(generic.ObjectDeleteView):
    queryset = models.NetworkTopologyCanvas.objects.all()


class DashboardView(TemplateView):
    """Dashboard view with network overview and visualization"""
    template_name = 'netbox_network_canvas_plugin/dashboard_simple.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get network statistics
        context.update({
            'device_count': Device.objects.count(),
            'canvas_count': models.NetworkTopologyCanvas.objects.count(),
            'vlan_count': VLAN.objects.count(),
            'cable_count': Cable.objects.count(),
        })
        
        # Get topology data for visualization
        topology_data = self._get_topology_data()
        context['topology_data_json'] = topology_data
        
        return context
    
    def _get_topology_data(self):
        """Get network topology data for visualization"""
        try:
            # Get devices with related data
            devices = Device.objects.select_related(
                'device_type', 'site', 'device_role'
            ).prefetch_related('interfaces').all()[:50]  # Limit for performance
            
            # Get cables/connections
            cables = Cable.objects.select_related(
                'a_terminations__device', 'b_terminations__device'
            ).all()[:100]  # Limit for performance
            
            # Serialize data
            devices_data = []
            for device in devices:
                devices_data.append({
                    'id': device.id,
                    'name': device.name,
                    'device_type': {
                        'model': device.device_type.model,
                        'manufacturer': device.device_type.manufacturer.name
                    },
                    'site': {
                        'name': device.site.name if device.site else 'Unknown'
                    },
                    'role': device.device_role.name if device.device_role else 'Unknown',
                    'status': device.status,
                    'interface_count': device.interfaces.count()
                })
            
            connections_data = []
            for cable in cables:
                if hasattr(cable, 'a_terminations') and hasattr(cable, 'b_terminations'):
                    connections_data.append({
                        'id': cable.id,
                        'type': cable.type,
                        'status': cable.status,
                        'length': cable.length,
                        'a_device': getattr(cable.a_terminations, 'device_id', None) if cable.a_terminations else None,
                        'b_device': getattr(cable.b_terminations, 'device_id', None) if cable.b_terminations else None,
                    })
            
            return {
                'devices': devices_data,
                'connections': connections_data,
                'stats': {
                    'total_devices': len(devices_data),
                    'total_connections': len(connections_data)
                }
            }
        except Exception as e:
            # Return minimal data on error
            return {
                'devices': [],
                'connections': [],
                'stats': {'total_devices': 0, 'total_connections': 0},
                'error': str(e)
            }


class TopologyDataView(View):
    """API endpoint for topology data"""
    
    def get(self, request):
        """Return topology data as JSON"""
        try:
            # Get query parameters
            site_id = request.GET.get('site')
            device_type = request.GET.get('device_type')
            limit = min(int(request.GET.get('limit', 100)), 500)  # Max 500 devices
            
            # Build device query
            device_query = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'device_role'
            ).prefetch_related('interfaces')
            
            if site_id:
                device_query = device_query.filter(site_id=site_id)
            
            if device_type:
                device_query = device_query.filter(device_type__model__icontains=device_type)
            
            devices = device_query[:limit]
            
            # Get interfaces and connections
            device_ids = [d.id for d in devices]
            interfaces = Interface.objects.filter(
                device_id__in=device_ids
            ).select_related('device')
            
            cables = Cable.objects.filter(
                a_terminations__device_id__in=device_ids
            ).select_related('a_terminations', 'b_terminations')[:200]
            
            # Serialize data
            response_data = {
                'devices': self._serialize_devices(devices),
                'interfaces': self._serialize_interfaces(interfaces),
                'connections': self._serialize_connections(cables),
                'metadata': {
                    'total_devices': len(devices),
                    'total_interfaces': len(interfaces),
                    'total_connections': len(cables),
                    'generated_at': str(timezone.now()) if 'timezone' in globals() else None
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'error': 'Failed to generate topology data',
                'message': str(e)
            }, status=500)
    
    def _serialize_devices(self, devices):
        """Serialize device data for JSON response"""
        return [{
            'id': device.id,
            'name': device.name,
            'display_name': str(device),
            'device_type': {
                'id': device.device_type.id,
                'model': device.device_type.model,
                'manufacturer': device.device_type.manufacturer.name,
                'slug': device.device_type.slug
            },
            'site': {
                'id': device.site.id if device.site else None,
                'name': device.site.name if device.site else 'Unknown',
                'slug': device.site.slug if device.site else None
            },
            'role': {
                'id': device.device_role.id if device.device_role else None,
                'name': device.device_role.name if device.device_role else 'Unknown',
                'slug': device.device_role.slug if device.device_role else None
            },
            'status': {
                'value': device.status,
                'label': device.get_status_display()
            },
            'primary_ip4': str(device.primary_ip4.address) if device.primary_ip4 else None,
            'primary_ip6': str(device.primary_ip6.address) if device.primary_ip6 else None,
        } for device in devices]
    
    def _serialize_interfaces(self, interfaces):
        """Serialize interface data"""
        return [{
            'id': interface.id,
            'name': interface.name,
            'device': interface.device.id,
            'device_name': interface.device.name,
            'type': interface.type,
            'enabled': interface.enabled,
            'connected': bool(interface.connected_endpoints),
        } for interface in interfaces]
    
    def _serialize_connections(self, cables):
        """Serialize connection/cable data"""
        connections = []
        for cable in cables:
            if cable.a_terminations and cable.b_terminations:
                connections.append({
                    'id': cable.id,
                    'type': cable.type,
                    'status': cable.status,
                    'length': float(cable.length) if cable.length else None,
                    'length_unit': cable.length_unit,
                    'a_termination': {
                        'device': getattr(cable.a_terminations, 'device_id', None),
                        'name': str(cable.a_terminations) if cable.a_terminations else None
                    },
                    'b_termination': {
                        'device': getattr(cable.b_terminations, 'device_id', None), 
                        'name': str(cable.b_terminations) if cable.b_terminations else None
                    }
                })
        return connections
