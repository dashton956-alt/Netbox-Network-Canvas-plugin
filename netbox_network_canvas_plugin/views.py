from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.utils import timezone
import json

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
            # Debug: Check if we can access Device model
            device_count = Device.objects.count()
            print(f"DEBUG: Found {device_count} devices in NetBox")
            
            # Get devices with related data
            devices = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'role'
            ).prefetch_related('interfaces').all()[:50]  # Limit for performance
            
            print(f"DEBUG: Retrieved {len(devices)} devices for visualization")
            
            # Get cables/connections
            cables = Cable.objects.all()[:100]  # Simplified query first
            print(f"DEBUG: Retrieved {len(cables)} cables")
            
            # Serialize data with better error handling
            devices_data = []
            for device in devices:
                try:
                    device_data = {
                        'id': device.id,
                        'name': device.name or f'Device-{device.id}',
                        'device_type': {
                            'model': getattr(device.device_type, 'model', 'Unknown') if device.device_type else 'Unknown',
                            'manufacturer': getattr(getattr(device.device_type, 'manufacturer', None), 'name', 'Unknown') if device.device_type and device.device_type.manufacturer else 'Unknown'
                        },
                        'site': {
                            'name': getattr(device.site, 'name', 'Unknown') if device.site else 'Unknown'
                        },
                        'role': getattr(device.role, 'name', 'Unknown') if device.role else 'Unknown',
                        'status': str(getattr(device, 'status', 'active')),
                        'interface_count': getattr(device, 'interfaces', []).count() if hasattr(device, 'interfaces') else 0
                    }
                    devices_data.append(device_data)
                    print(f"DEBUG: Processed device {device.name}")
                except Exception as device_error:
                    print(f"DEBUG: Error processing device {device}: {device_error}")
                    # Add a minimal device entry
                    devices_data.append({
                        'id': device.id,
                        'name': getattr(device, 'name', f'Device-{device.id}'),
                        'device_type': {'model': 'Unknown', 'manufacturer': 'Unknown'},
                        'site': {'name': 'Unknown'},
                        'role': 'Unknown',
                        'status': 'active',
                        'interface_count': 0
                    })
            
            # Process cables to extract real device connections
            # Process cables with improved connection detection
            connections_data = []
            for cable in cables:
                try:
                    # Get cable terminations to find connected devices
                    a_device_id = None
                    b_device_id = None
                    
                    # Handle different types of cable terminations
                    if hasattr(cable, 'a_terminations'):
                        for termination in cable.a_terminations.all():
                            if hasattr(termination, 'device') and termination.device:
                                a_device_id = termination.device.id
                                break
                            elif hasattr(termination, '_device') and termination._device:
                                a_device_id = termination._device.id
                                break
                    
                    if hasattr(cable, 'b_terminations'):
                        for termination in cable.b_terminations.all():
                            if hasattr(termination, 'device') and termination.device:
                                b_device_id = termination.device.id
                                break
                            elif hasattr(termination, '_device') and termination._device:
                                b_device_id = termination._device.id
                                break
                    
                    # Only add connection if we have both devices
                    if a_device_id and b_device_id and a_device_id != b_device_id:
                        connections_data.append({
                            'id': cable.id,
                            'type': str(getattr(cable, 'type', 'ethernet')),
                            'status': str(getattr(cable, 'status', 'connected')),
                            'length': getattr(cable, 'length', None),
                            'a_device': a_device_id,
                            'b_device': b_device_id,
                        })
                        print(f"DEBUG: Found connection between devices {a_device_id} and {b_device_id}")
                    
                except Exception as cable_error:
                    print(f"DEBUG: Error processing cable {cable.id}: {cable_error}")
                    continue
            
            print(f"DEBUG: Found {len(connections_data)} real connections")
            
            result = {
                'devices': devices_data,
                'connections': connections_data,
                'stats': {
                    'total_devices': len(devices_data),
                    'total_connections': len(connections_data)
                }
            }
            
            print(f"DEBUG: Final result has {len(result['devices'])} devices")
            return result
            
        except Exception as e:
            print(f"DEBUG: Major error in _get_topology_data: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Emergency fallback - try to get ANY device data
            try:
                devices = list(Device.objects.all()[:10])
                print(f"DEBUG: Emergency fallback found {len(devices)} devices")
                
                simple_devices = []
                for i, device in enumerate(devices):
                    simple_devices.append({
                        'id': getattr(device, 'id', i),
                        'name': getattr(device, 'name', f'Device-{i}'),
                        'device_type': {'model': 'Unknown', 'manufacturer': 'Unknown'},
                        'site': {'name': 'Unknown'},
                        'role': 'Unknown',
                        'status': 'active',
                        'interface_count': 0
                    })
                
                return {
                    'devices': simple_devices,
                    'connections': [],
                    'stats': {'total_devices': len(simple_devices), 'total_connections': 0},
                    'error': f'Partial data due to error: {str(e)}'
                }
            except Exception as fallback_error:
                print(f"DEBUG: Even fallback failed: {fallback_error}")
                return {
                    'devices': [],
                    'connections': [],
                    'stats': {'total_devices': 0, 'total_connections': 0},
                    'error': f'Complete failure: {str(e)} | Fallback: {str(fallback_error)}'
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
