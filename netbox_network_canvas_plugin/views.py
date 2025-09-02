import json
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
        context['topology_data_json'] = json.dumps(topology_data)
        
        return context
    
    def _get_topology_data(self):
        """Get network topology data for visualization"""
        try:
            # Get devices with related data, grouped by site
            devices = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'role'
            ).prefetch_related('interfaces').all()[:50]  # Limit for performance
            
            # Group devices by site
            sites_data = {}
            for device in devices:
                site_name = device.site.name if device.site else 'Unknown Site'
                if site_name not in sites_data:
                    sites_data[site_name] = {
                        'name': site_name,
                        'devices': []
                    }
                
                # Determine device type and icon
                device_type = self._get_device_type(device)
                
                device_data = {
                    'id': device.id,
                    'name': device.name,
                    'device_type': {
                        'model': device.device_type.model if device.device_type else 'Unknown',
                        'manufacturer': device.device_type.manufacturer.name if device.device_type and device.device_type.manufacturer else 'Unknown'
                    },
                    'site': {
                        'name': device.site.name if device.site else 'Unknown'
                    },
                    'role': device.role.name if device.role else 'Unknown',
                    'status': str(device.status) if device.status else 'unknown',
                    'interface_count': device.interfaces.count(),
                    'type': device_type,  # Enhanced device type
                    'icon': self._get_device_icon(device_type)
                }
                sites_data[site_name]['devices'].append(device_data)
            
            # Convert to list format
            sites_list = list(sites_data.values())
            all_devices = []
            for site in sites_list:
                all_devices.extend(site['devices'])
            
            return {
                'devices': all_devices,
                'sites': sites_list,
                'connections': [],  # Empty for now
                'stats': {
                    'total_devices': len(all_devices),
                    'total_sites': len(sites_list),
                    'total_connections': 0
                }
            }
        except Exception as e:
            # Return minimal data on error
            return {
                'devices': [],
                'sites': [],
                'connections': [],
                'stats': {'total_devices': 0, 'total_sites': 0, 'total_connections': 0},
                'error': str(e)
            }

    def _get_device_type(self, device):
        """Determine device type from device model and role"""
        if not device.device_type:
            return 'unknown'
        
        model = device.device_type.model.lower()
        role = device.role.name.lower() if device.role else ''
        
        # Check role first for more accurate typing
        if 'switch' in role:
            return 'switch'
        elif 'router' in role:
            return 'router'
        elif 'firewall' in role or 'security' in role:
            return 'firewall'
        elif 'access point' in role or 'ap' in role or 'wireless' in role:
            return 'ap'
        elif 'server' in role or 'vm' in role or 'virtual' in role:
            return 'server'
        
        # Fallback to model name detection
        if any(x in model for x in ['switch', 'catalyst', 'nexus', 'ex-', 'qfx']):
            return 'switch'
        elif any(x in model for x in ['router', 'isr', 'asr', 'mx-', 'srx']):
            return 'router'
        elif any(x in model for x in ['firewall', 'pa-', 'asa', 'fortigate']):
            return 'firewall'
        elif any(x in model for x in ['ap-', 'access point', 'wireless', 'wifi']):
            return 'ap'
        elif any(x in model for x in ['server', 'poweredge', 'proliant', 'vm']):
            return 'server'
        
        return 'unknown'

    def _get_device_icon(self, device_type):
        """Get icon for device type"""
        icons = {
            'switch': '⚡',
            'router': '🔀', 
            'firewall': '🛡️',
            'ap': '📶',
            'server': '💻',
            'vm': '🖥️',
            'unknown': '❓'
        }
        return icons.get(device_type, icons['unknown'])


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
                'device_type', 'device_type__manufacturer', 'site', 'role'
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
            
            # For now, return empty connections to avoid termination issues
            cables = []
            
            # Serialize data
            response_data = {
                'devices': self._serialize_devices(devices),
                'interfaces': self._serialize_interfaces(interfaces),
                'connections': [],  # Simplified for now
                'metadata': {
                    'total_devices': len(devices),
                    'total_interfaces': len(interfaces),
                    'total_connections': 0,
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
                'id': device.device_type.id if device.device_type else None,
                'model': device.device_type.model if device.device_type else 'Unknown',
                'manufacturer': device.device_type.manufacturer.name if device.device_type and device.device_type.manufacturer else 'Unknown',
                'slug': device.device_type.slug if device.device_type else None
            },
            'site': {
                'id': device.site.id if device.site else None,
                'name': device.site.name if device.site else 'Unknown',
                'slug': device.site.slug if device.site else None
            },
            'role': {
                'id': device.role.id if device.role else None,
                'name': device.role.name if device.role else 'Unknown',
                'slug': device.role.slug if device.role else None
            },
            'status': {
                'value': str(device.status) if device.status else 'unknown',
                'label': device.get_status_display() if hasattr(device, 'get_status_display') else str(device.status)
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
