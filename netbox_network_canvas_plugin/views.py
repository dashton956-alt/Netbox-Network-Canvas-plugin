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
    template_name = 'netbox_network_canvas_plugin/dashboard_improved.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get network statistics with error handling
            from dcim.models import Site, DeviceType
            
            context.update({
                'device_count': Device.objects.count(),
                'canvas_count': models.NetworkTopologyCanvas.objects.count(),
                'vlan_count': VLAN.objects.count(),
                'cable_count': Cable.objects.count(),
                'site_count': Site.objects.count(),
                'device_type_count': DeviceType.objects.count(),
            })
            
            # Get topology data for visualization
            topology_data = self._get_topology_data()
            context['topology_data_json'] = json.dumps(topology_data)
            
        except Exception as e:
            # Provide fallback data if there are database errors
            print(f"Error in DashboardView: {e}")
            context.update({
                'device_count': 0,
                'canvas_count': 0,
                'vlan_count': 0,
                'cable_count': 0,
                'site_count': 0,
                'device_type_count': 0,
                'topology_data_json': json.dumps({'devices': [], 'connections': [], 'stats': {'total_devices': 0, 'total_connections': 0}})
            })
        
        return context
        
        return context
    
    def _get_topology_data(self):
        """Get network topology data for visualization"""
        try:
            print("DEBUG: Starting _get_topology_data method")
            
            # Check database connectivity first
            try:
                device_count = Device.objects.count()
                print(f"DEBUG: Found {device_count} devices in NetBox")
            except Exception as db_error:
                print(f"DEBUG: Database connectivity error: {db_error}")
                raise
            
            # If no devices, return empty structure
            if device_count == 0:
                print("DEBUG: No devices found, returning empty data")
                return {
                    'devices': [],
                    'connections': [],
                    'stats': {'total_devices': 0, 'total_connections': 0}
                }
            
            # Get devices with safe query
            try:
                devices = Device.objects.select_related(
                    'device_type__manufacturer', 'site', 'role'
                ).prefetch_related('interfaces')[:20]  # Smaller limit for safety
                print(f"DEBUG: Retrieved {len(devices)} devices for visualization")
            except Exception as query_error:
                print(f"DEBUG: Device query error: {query_error}")
                # Try simpler query
                devices = Device.objects.all()[:10]
                print(f"DEBUG: Retrieved {len(devices)} devices with simple query")
            
            # Serialize data with comprehensive error handling
            devices_data = []
            for i, device in enumerate(devices):
                try:
                    device_data = {
                        'id': device.id,
                        'name': getattr(device, 'name', f'Device-{device.id}'),
                        'device_type': {
                            'model': getattr(device.device_type, 'model', 'Unknown') if hasattr(device, 'device_type') and device.device_type else 'Unknown',
                            'manufacturer': 'Unknown'
                        },
                        'site': {
                            'name': getattr(device.site, 'name', f'Site-{i}') if hasattr(device, 'site') and device.site else f'Site-{i}'
                        },
                        'role': getattr(device.role, 'name', 'Unknown') if hasattr(device, 'role') and device.role else 'Unknown',
                        'status': 'active',
                        'interface_count': 0
                    }
                    
                    # Try to get manufacturer safely
                    try:
                        if hasattr(device, 'device_type') and device.device_type and hasattr(device.device_type, 'manufacturer') and device.device_type.manufacturer:
                            device_data['device_type']['manufacturer'] = device.device_type.manufacturer.name
                    except:
                        pass
                    
                    devices_data.append(device_data)
                    print(f"DEBUG: Successfully processed device {device_data['name']}")
                    
                except Exception as device_error:
                    print(f"DEBUG: Error processing device {i}: {device_error}")
                    # Add minimal device entry
                    devices_data.append({
                        'id': getattr(device, 'id', i),
                        'name': f'Device-{i}',
                        'device_type': {'model': 'Unknown', 'manufacturer': 'Unknown'},
                        'site': {'name': f'Site-{i}'},
                        'role': 'Unknown',
                        'status': 'active',
                        'interface_count': 0
                    })
            
            # Create simple logical connections if we have devices
            connections_data = []
            if len(devices_data) > 1:
                try:
                    connections_data = self._create_logical_connections(devices_data)
                    print(f"DEBUG: Created {len(connections_data)} logical connections")
                except Exception as conn_error:
                    print(f"DEBUG: Error creating connections: {conn_error}")
                    connections_data = []
            
            result = {
                'devices': devices_data,
                'connections': connections_data,
                'stats': {
                    'total_devices': len(devices_data),
                    'total_connections': len(connections_data)
                }
            }
            
            print(f"DEBUG: Returning data with {len(result['devices'])} devices and {len(result['connections'])} connections")
            return result
            
        except Exception as e:
            print(f"DEBUG: Major error in _get_topology_data: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return minimal data structure for safety
            return {
                'devices': [],
                'connections': [],
                'stats': {
                    'total_devices': 0,
                    'total_connections': 0
                }
            }

    def _create_logical_connections(self, devices_data):
        """Create logical network connections for visualization when no physical cables exist"""
        connections = []
        connection_id = 1000  # Start with high ID to avoid conflicts
        
        # Group devices by site and role for logical connectivity
        sites = {}
        for device in devices_data:
            site_name = device['site']['name']
            if site_name not in sites:
                sites[site_name] = {'core': [], 'dist': [], 'access': [], 'routers': [], 'firewalls': [], 'servers': [], 'wireless': [], 'others': []}
            
            role = device['role'].lower()
            device_type = device['device_type']['model'].lower()
            
            # Categorize devices
            if 'core' in role or ('switch' in role and 'core' in device_type):
                sites[site_name]['core'].append(device)
            elif 'distribution' in role or ('switch' in role and ('dist' in device_type or '9400' in device_type)):
                sites[site_name]['dist'].append(device)  
            elif 'access' in role or ('switch' in role and ('access' in device_type or '9200' in device_type)):
                sites[site_name]['access'].append(device)
            elif 'router' in role or 'isr' in device_type or 'asr' in device_type:
                sites[site_name]['routers'].append(device)
            elif 'firewall' in role or 'asa' in device_type or 'srx' in device_type or 'pa-' in device_type:
                sites[site_name]['firewalls'].append(device)
            elif 'server' in role or 'poweredge' in device_type or 'proliant' in device_type:
                sites[site_name]['servers'].append(device)
            elif 'wireless' in role or 'access point' in role or 'wlc' in device_type or 'ap' in device['name'].lower():
                sites[site_name]['wireless'].append(device)
            else:
                sites[site_name]['others'].append(device)
        
        # Create logical connections for each site
        for site_name, site_devices in sites.items():
            # Core to Distribution
            for core in site_devices['core']:
                for dist in site_devices['dist']:
                    connections.append({
                        'id': connection_id,
                        'type': 'ethernet',
                        'status': 'connected',
                        'length': None,
                        'a_device': core['id'],
                        'b_device': dist['id']
                    })
                    connection_id += 1
            
            # Distribution to Access
            for dist in site_devices['dist']:
                for access in site_devices['access']:
                    connections.append({
                        'id': connection_id,
                        'type': 'ethernet', 
                        'status': 'connected',
                        'length': None,
                        'a_device': dist['id'],
                        'b_device': access['id']
                    })
                    connection_id += 1
                    
            # Routers to Core/Firewalls
            for router in site_devices['routers']:
                # Connect to core switches
                for core in site_devices['core'][:1]:  # Just first core
                    connections.append({
                        'id': connection_id,
                        'type': 'ethernet',
                        'status': 'connected', 
                        'length': None,
                        'a_device': router['id'],
                        'b_device': core['id']
                    })
                    connection_id += 1
                    
                # Connect to firewalls
                for fw in site_devices['firewalls'][:1]:  # Just first firewall
                    connections.append({
                        'id': connection_id,
                        'type': 'ethernet',
                        'status': 'connected',
                        'length': None,
                        'a_device': router['id'],
                        'b_device': fw['id']
                    })
                    connection_id += 1
            
            # Wireless Controllers to Distribution/Core
            for wireless in site_devices['wireless']:
                if 'wlc' in wireless['name'].lower() or 'controller' in wireless['role'].lower():
                    # Connect WLC to distribution/core
                    target_switches = site_devices['dist'] + site_devices['core']
                    if target_switches:
                        connections.append({
                            'id': connection_id,
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_device': wireless['id'],
                            'b_device': target_switches[0]['id']
                        })
                        connection_id += 1
        
        print(f"DEBUG: Created {len(connections)} logical connections")
        return connections

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


class TopologyDataView(View):
    """API view for topology data"""
    
    def get(self, request):
        """Get topology data as JSON"""
        try:
            # Use the same method from DashboardView
            dashboard_view = DashboardView()
            topology_data = dashboard_view._get_topology_data()
            return JsonResponse(topology_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
