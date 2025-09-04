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
        context.update({
            'topology_data': topology_data,
            'topology_data_json': json.dumps(topology_data, default=str)
        })
        
        return context
    
    def _get_topology_data(self):
        """Get basic network topology data"""
        try:
            devices = Device.objects.select_related('device_type', 'site', 'role').all()[:50]
            
            topology_data = {
                'devices': [
                    {
                        'id': device.id,
                        'name': device.name,
                        'type': device.device_type.model if device.device_type else 'Unknown',
                        'site': device.site.name if device.site else 'No Site',
                        'role': device.role.name if device.role else 'Unknown Role',
                        'x': None,  # Will be calculated by frontend
                        'y': None   # Will be calculated by frontend
                    }
                    for device in devices
                ],
                'connections': []  # Simplified for now
            }
            
            return topology_data
            
        except Exception as e:
            print(f"Error getting topology data: {e}")
            return {
                'devices': [],
                'connections': []
            }


class EnhancedDashboardView(TemplateView):
    """Enhanced dashboard view with hierarchical network visualization"""
    template_name = 'netbox_network_canvas_plugin/dashboard_enhanced_v0.1.4_style.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get network statistics
        context.update({
            'device_count': Device.objects.count(),
            'canvas_count': models.NetworkTopologyCanvas.objects.count(),
            'vlan_count': VLAN.objects.count(),
            'cable_count': Cable.objects.count(),
        })
        
        # Get enhanced topology data
        topology_data = self._get_enhanced_topology_data()
        context.update({
            'topology_data': topology_data,
            'topology_data_json': json.dumps(topology_data, default=str)
        })
        
        return context
    
    def _get_enhanced_topology_data(self):
        """Get enhanced network topology data with better connection detection"""
        print("=== _get_enhanced_topology_data called ===")
        
        try:
            # Get devices with related data - remove restrictive status filter
            devices = Device.objects.select_related(
                'device_type', 'device_type__manufacturer', 'site', 'role', 'primary_ip4', 'primary_ip6'
            ).prefetch_related('interfaces').all()[:300]  # Get all devices, not just active
            
            # Debug logging
            total_devices = len(devices)
            devices_with_sites = len([d for d in devices if d.site])
            print(f"Total devices found: {total_devices}")
            print(f"Devices with sites: {devices_with_sites}")
            
            # Process sites
            sites_dict = {}
            for device in devices:
                if device.site and device.site.id not in sites_dict:
                    sites_dict[device.site.id] = {
                        'id': device.site.id,
                        'name': device.site.name,
                        'slug': device.site.slug,
                        'devices': []
                    }
            
            sites = list(sites_dict.values())
            print(f"Sites found: {len(sites)}")
            for site in sites:
                print(f"  Site: {site['name']} (ID: {site['id']})")
            
            # Process devices
            processed_devices = []
            for device in devices:
                try:
                    device_data = {
                        'id': device.id,
                        'name': device.name,
                        'site_id': device.site.id if device.site else None,
                        'site_name': device.site.name if device.site else 'No Site',
                        'device_type': device.device_type.model if device.device_type else 'Unknown',
                        'device_role': device.role.name if device.role else 'Unknown',
                        'manufacturer': device.device_type.manufacturer.name if device.device_type and device.device_type.manufacturer else 'Unknown',
                        'status': device.status,
                        'primary_ip': str(device.primary_ip4 or device.primary_ip6) if (device.primary_ip4 or device.primary_ip6) else None,
                        'interface_count': device.interfaces.count(),
                    }
                    processed_devices.append(device_data)
                    
                    # Add device to its site
                    if device.site and device.site.id in sites_dict:
                        sites_dict[device.site.id]['devices'].append(device_data)
                        
                except Exception as e:
                    print(f"Error processing device {device.name}: {e}")
                    continue
            
            print(f"Processed devices: {len(processed_devices)}")
            
            # Update sites list to include device counts
            sites = list(sites_dict.values())
            for site in sites:
                device_count = len(site['devices'])
                print(f"  Site '{site['name']}' has {device_count} devices")
            
            # Optionally include empty sites by querying all sites
            try:
                from dcim.models import Site
                all_sites = Site.objects.all()
                for site_obj in all_sites:
                    if site_obj.id not in sites_dict:
                        sites.append({
                            'id': site_obj.id,
                            'name': site_obj.name,
                            'slug': site_obj.slug,
                            'devices': []
                        })
                        print(f"  Added empty site: {site_obj.name}")
            except Exception as e:
                print(f"Error getting all sites: {e}")
            
            # For now, skip complex connection logic to focus on layout
            connections = []
            
            return {
                'devices': processed_devices,
                'sites': sites,
                'connections': connections,
                'debug': {
                    'total_devices_queried': total_devices,
                    'devices_with_sites': devices_with_sites,
                    'devices_processed': len(processed_devices),
                    'sites_created': len(sites),
                    'connections_found': len(connections),
                    'method_used': 'real_netbox_data'
                }
            }
            
        except Exception as e:
            print(f"Error in _get_enhanced_topology_data: {e}")
            return {
                'devices': [],
                'sites': [],
                'connections': [],
                'debug': {
                    'error': str(e),
                    'method_used': 'error_fallback'
                }
            }


class NetworkTopologyApiView(View):
    """API endpoint for getting network topology data"""
    
    def get(self, request):
        """Return JSON topology data"""
        try:
            # Get enhanced topology data
            enhanced_view = EnhancedDashboardView()
            topology_data = enhanced_view._get_enhanced_topology_data()
            
            return JsonResponse(topology_data)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'devices': [],
                'sites': [],
                'connections': []
            }, status=500)


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
                'total_interfaces': Interface.objects.count(),
                'connected_interfaces': Interface.objects.exclude(connected_endpoints__isnull=True).count(),
            }
            
            # Sample devices
            sample_devices = Device.objects.select_related('device_type', 'site', 'role')[:10]
            debug_info['sample_devices'] = [
                {
                    'id': device.id,
                    'name': device.name,
                    'site': device.site.name if device.site else None,
                    'type': device.device_type.model if device.device_type else None,
                    'role': device.role.name if device.role else None,
                    'status': str(device.status)
                }
                for device in sample_devices
            ]
            
            return JsonResponse(debug_info)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Failed to retrieve debug information'
            }, status=500)


class CableDebugView(View):
    """Debug endpoint specifically for cable connection analysis"""
    
    def get(self, request):
        """Return detailed cable and connection debug information"""
        try:
            debug_info = {
                'total_cables': Cable.objects.count(),
                'cable_details': []
            }
            
            # Get sample cables with detailed analysis
            cables = Cable.objects.prefetch_related('a_terminations', 'b_terminations')[:10]
            
            for cable in cables:
                cable_detail = {
                    'id': cable.id,
                    'type': str(cable.type) if cable.type else None,
                    'status': str(cable.status) if cable.status else None,
                    'a_terminations_count': cable.a_terminations.count(),
                    'b_terminations_count': cable.b_terminations.count(),
                    'a_terminations': [],
                    'b_terminations': []
                }
                
                # Analyze A terminations
                for term in cable.a_terminations.all()[:3]:  # First 3 only
                    term_info = {
                        'type': type(term).__name__,
                        'id': term.id,
                        'object_type': str(term.object_type) if hasattr(term, 'object_type') else None,
                    }
                    
                    if hasattr(term, 'termination') and term.termination:
                        term_info['termination_type'] = type(term.termination).__name__
                        if hasattr(term.termination, 'device'):
                            term_info['device_id'] = term.termination.device.id if term.termination.device else None
                            term_info['device_name'] = term.termination.device.name if term.termination.device else None
                    
                    cable_detail['a_terminations'].append(term_info)
                
                # Analyze B terminations
                for term in cable.b_terminations.all()[:3]:  # First 3 only
                    term_info = {
                        'type': type(term).__name__,
                        'id': term.id,
                        'object_type': str(term.object_type) if hasattr(term, 'object_type') else None,
                    }
                    
                    if hasattr(term, 'termination') and term.termination:
                        term_info['termination_type'] = type(term.termination).__name__
                        if hasattr(term.termination, 'device'):
                            term_info['device_id'] = term.termination.device.id if term.termination.device else None
                            term_info['device_name'] = term.termination.device.name if term.termination.device else None
                    
                    cable_detail['b_terminations'].append(term_info)
                
                debug_info['cable_details'].append(cable_detail)
            
            return JsonResponse(debug_info)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Failed to retrieve cable debug information'
            }, status=500)


class TopologyDataView(View):
    """API endpoint for topology data - alias for NetworkTopologyApiView for backward compatibility"""
    
    def get(self, request):
        """Return JSON topology data"""
        # Delegate to the NetworkTopologyApiView
        api_view = NetworkTopologyApiView()
        return api_view.get(request)
