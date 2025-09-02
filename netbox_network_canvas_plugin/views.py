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
            # Get all active devices with related data, grouped by site
            devices = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'role'
            ).prefetch_related('interfaces').filter(
                status='active'  # Only active devices
            ).all()[:200]  # Increased limit for better coverage
            
            # Get connections/cables between devices
            device_ids = [d.id for d in devices]
            cables = Cable.objects.filter(
                a_terminations__device_id__in=device_ids,
                b_terminations__device_id__in=device_ids
            ).select_related().distinct()[:100]  # Limit cables for performance
            
            # Group devices by site
            sites_data = {}
            for device in devices:
                site_name = device.site.name if device.site else 'Unknown Site'
                if site_name not in sites_data:
                    sites_data[site_name] = {
                        'name': site_name,
                        'id': device.site.id if device.site else None,
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
                        'id': device.site.id if device.site else None,
                        'name': device.site.name if device.site else 'Unknown'
                    },
                    'role': device.role.name if device.role else 'Unknown',
                    'status': str(device.status) if device.status else 'unknown',
                    'interface_count': device.interfaces.count(),
                    'type': device_type,  # Enhanced device type
                    'icon': self._get_device_icon(device_type),
                    'primary_ip': str(device.primary_ip4.address) if device.primary_ip4 else None
                }
                sites_data[site_name]['devices'].append(device_data)
            
            # Process connections
            connections = []
            for cable in cables:
                try:
                    # Get termination devices
                    a_device_id = None
                    b_device_id = None
                    
                    # Handle different termination types
                    if hasattr(cable, 'a_terminations') and cable.a_terminations:
                        for termination in cable.a_terminations.all():
                            if hasattr(termination, 'device'):
                                a_device_id = termination.device.id
                                break
                    
                    if hasattr(cable, 'b_terminations') and cable.b_terminations:
                        for termination in cable.b_terminations.all():
                            if hasattr(termination, 'device'):
                                b_device_id = termination.device.id
                                break
                    
                    if a_device_id and b_device_id and a_device_id in device_ids and b_device_id in device_ids:
                        connections.append({
                            'id': cable.id,
                            'source': a_device_id,
                            'target': b_device_id,
                            'type': str(cable.type) if cable.type else 'ethernet',
                            'status': str(cable.status) if cable.status else 'connected',
                            'length': float(cable.length) if cable.length else None
                        })
                except Exception as e:
                    # Skip problematic cables
                    print(f"Skipping cable {cable.id}: {e}")
                    continue
            
            # Convert to list format
            sites_list = list(sites_data.values())
            all_devices = []
            for site in sites_list:
                all_devices.extend(site['devices'])
            
            return {
                'devices': all_devices,
                'sites': sites_list,
                'connections': connections,
                'stats': {
                    'total_devices': len(all_devices),
                    'total_sites': len(sites_list),
                    'total_connections': len(connections)
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


class EnhancedDashboardView(TemplateView):
    """Enhanced dashboard view with draggable/resizable sites and better connection detection"""
    template_name = 'netbox_network_canvas_plugin/dashboard_enhanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get network statistics
        context.update({
            'device_count': Device.objects.count(),
            'canvas_count': models.NetworkTopologyCanvas.objects.count(),
            'vlan_count': VLAN.objects.count(),
            'cable_count': Cable.objects.count(),
        })
        
        # Get enhanced topology data for visualization
        topology_data = self._get_enhanced_topology_data()
        context['topology_data_json'] = json.dumps(topology_data)
        
        return context
    
    def _get_enhanced_topology_data(self):
        """Get enhanced network topology data with better connection detection"""
        try:
            # Get devices with related data - remove restrictive status filter
            devices = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'role', 'primary_ip4', 'primary_ip6'
            ).prefetch_related('interfaces').all()[:300]  # Get all devices, not just active
            
            print(f"Enhanced query found {len(devices)} total devices")
            
            # Debug: Check device statuses
            if devices:
                statuses = set(str(d.status) for d in devices)
                print(f"Device statuses found: {statuses}")
            
            device_ids = [d.id for d in devices]
            
            # Enhanced cable detection with better termination handling
            cables = []
            try:
                # Get cables connected to our devices
                raw_cables = Cable.objects.filter(
                    a_terminations__device_id__in=device_ids
                ).distinct()[:200] | Cable.objects.filter(
                    b_terminations__device_id__in=device_ids
                ).distinct()[:200]
                
                cables = list(raw_cables.distinct())
                print(f"Found {len(cables)} cables for {len(devices)} devices")
                
            except Exception as e:
                print(f"Cable query error: {e}")
                cables = []
            
            # Group devices by site with enhanced organization
            sites_data = {}
            for device in devices:
                site_name = device.site.name if device.site else 'Unknown Site'
                site_id = device.site.id if device.site else None
                
                if site_name not in sites_data:
                    sites_data[site_name] = {
                        'name': site_name,
                        'id': site_id,
                        'devices': []
                    }
                
                # Enhanced device type detection
                device_type = self._get_device_type(device)
                
                device_data = {
                    'id': device.id,
                    'name': device.name,
                    'device_type': {
                        'model': device.device_type.model if device.device_type else 'Unknown',
                        'manufacturer': device.device_type.manufacturer.name if device.device_type and device.device_type.manufacturer else 'Unknown'
                    },
                    'site': {
                        'id': site_id,
                        'name': site_name
                    },
                    'role': device.role.name if device.role else 'Unknown',
                    'status': str(device.status) if device.status else 'unknown',
                    'interface_count': device.interfaces.count(),
                    'type': device_type,
                    'icon': self._get_device_icon(device_type),
                    'primary_ip': str(device.primary_ip4.address) if device.primary_ip4 else (
                        str(device.primary_ip6.address) if device.primary_ip6 else None
                    )
                }
                sites_data[site_name]['devices'].append(device_data)
            
            # Enhanced connection processing
            connections = []
            for cable in cables:
                try:
                    connection = self._process_cable_connection(cable, device_ids)
                    if connection:
                        connections.append(connection)
                except Exception as e:
                    print(f"Error processing cable {cable.id}: {e}")
                    continue
            
            # Convert to list format
            sites_list = list(sites_data.values())
            all_devices = []
            for site in sites_list:
                all_devices.extend(site['devices'])
            
            print(f"Enhanced topology: {len(all_devices)} devices, {len(connections)} connections, {len(sites_list)} sites")
            
            return {
                'devices': all_devices,
                'sites': sites_list,
                'connections': connections,
                'stats': {
                    'total_devices': len(all_devices),
                    'total_sites': len(sites_list),
                    'total_connections': len(connections)
                }
            }
            
        except Exception as e:
            print(f"Enhanced topology data error: {e}")
            return {
                'devices': [],
                'sites': [],
                'connections': [],
                'stats': {'total_devices': 0, 'total_sites': 0, 'total_connections': 0},
                'error': str(e)
            }
    
    def _process_cable_connection(self, cable, device_ids):
        """Process a cable to extract device-to-device connections"""
        try:
            a_device_id = None
            b_device_id = None
            a_interface = None
            b_interface = None
            
            # Handle A terminations
            if hasattr(cable, 'a_terminations'):
                for termination in cable.a_terminations.all():
                    if hasattr(termination, 'device') and termination.device.id in device_ids:
                        a_device_id = termination.device.id
                        a_interface = termination.name if hasattr(termination, 'name') else str(termination)
                        break
            
            # Handle B terminations  
            if hasattr(cable, 'b_terminations'):
                for termination in cable.b_terminations.all():
                    if hasattr(termination, 'device') and termination.device.id in device_ids:
                        b_device_id = termination.device.id
                        b_interface = termination.name if hasattr(termination, 'name') else str(termination)
                        break
            
            # Return connection if both ends found
            if a_device_id and b_device_id and a_device_id != b_device_id:
                return {
                    'id': cable.id,
                    'source': a_device_id,
                    'target': b_device_id,
                    'type': str(cable.type) if cable.type else 'ethernet',
                    'status': str(cable.status) if cable.status else 'connected',
                    'length': float(cable.length) if cable.length else None,
                    'a_interface': a_interface,
                    'b_interface': b_interface
                }
            
            return None
            
        except Exception as e:
            print(f"Cable processing error for cable {cable.id}: {e}")
            return None


class DebugDataView(View):
    """Debug endpoint to check NetBox data availability"""
    
    def get(self, request):
        """Return debug information about NetBox data"""
        try:
            debug_info = {
                'total_devices': Device.objects.count(),
                'devices_with_sites': Device.objects.exclude(site__isnull=True).count(),
                'total_sites': Device.objects.values('site__name').distinct().count(),
                'total_cables': Cable.objects.count(),
            }
            
            # Get device statuses
            device_statuses = {}
            for device in Device.objects.all()[:50]:
                status = str(device.status)
                device_statuses[status] = device_statuses.get(status, 0) + 1
            
            debug_info['device_statuses'] = device_statuses
            
            # Get sample devices
            sample_devices = []
            for device in Device.objects.select_related('site', 'device_type', 'role')[:10]:
                sample_devices.append({
                    'id': device.id,
                    'name': device.name,
                    'site': device.site.name if device.site else None,
                    'status': str(device.status),
                    'device_type': device.device_type.model if device.device_type else None,
                    'role': device.role.name if device.role else None,
                })
            
            debug_info['sample_devices'] = sample_devices
            
            # Get site information
            sites = []
            from django.db.models import Count
            site_data = Device.objects.values('site__name').annotate(
                device_count=Count('id')
            ).order_by('-device_count')[:10]
            
            for site in site_data:
                if site['site__name']:
                    sites.append({
                        'name': site['site__name'],
                        'device_count': site['device_count']
                    })
            
            debug_info['sites'] = sites
            
            return JsonResponse(debug_info, indent=2)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Debug data collection failed'
            }, status=500)


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
