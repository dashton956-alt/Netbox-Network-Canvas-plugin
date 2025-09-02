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
            
            # Debug logging
            total_devices = len(devices)
            devices_with_sites = len([d for d in devices if d.site])
            devices_without_sites = total_devices - devices_with_sites
            
            # Create debug info that will be returned in the data
            debug_info = {
                'total_devices_queried': total_devices,
                'devices_with_sites': devices_with_sites,
                'devices_without_sites': devices_without_sites,
                'device_statuses': {},
                'sample_devices': []
            }
            
            # Check device statuses
            status_counts = {}
            for device in devices[:10]:  # Sample first 10 devices
                status = str(device.status)
                status_counts[status] = status_counts.get(status, 0) + 1
                debug_info['sample_devices'].append({
                    'id': device.id,
                    'name': device.name,
                    'site': device.site.name if device.site else None,
                    'status': status,
                    'has_device_type': bool(device.device_type),
                    'has_role': bool(device.role)
                })
            
            debug_info['device_statuses'] = status_counts
            
            device_ids = [d.id for d in devices]
            
            # Enhanced cable detection with multiple approaches
            cables = []
            connections_debug = {
                'method_used': 'none',
                'total_cables_found': 0,
                'device_connections': 0,
                'circuit_connections': 0
            }
            
            try:
                # Method 1: Try direct cable query first
                all_cables = Cable.objects.select_related().prefetch_related(
                    'a_terminations__termination',
                    'b_terminations__termination'
                ).all()[:100]  # Limit for performance
                connections_debug['total_cables_found'] = len(all_cables)
                
                # Debug: Log cable information
                debug_info['cable_details'] = []
                for i, cable in enumerate(all_cables[:5]):  # Sample first 5 cables
                    cable_detail = {
                        'id': cable.id,
                        'type': str(cable.type) if cable.type else 'No Type',
                        'status': str(cable.status) if cable.status else 'No Status',
                        'a_terminations': [],
                        'b_terminations': []
                    }
                    
                    # Analyze A terminations in detail
                    try:
                        a_terms = list(cable.a_terminations.all())
                        cable_detail['a_terminations_count'] = len(a_terms)
                        for term in a_terms[:2]:  # First 2 terminations
                            term_info = {
                                'term_type': type(term).__name__,
                                'has_termination': hasattr(term, 'termination'),
                            }
                            
                            # Check multiple ways to access the device
                            if hasattr(term, 'termination') and term.termination:
                                term_info['termination_type'] = type(term.termination).__name__
                                if hasattr(term.termination, 'device') and term.termination.device:
                                    term_info['device_id'] = term.termination.device.id
                                    term_info['device_name'] = term.termination.device.name
                                    term_info['interface_name'] = getattr(term.termination, 'name', 'No Name')
                                    term_info['in_our_devices'] = term.termination.device.id in device_ids
                            elif hasattr(term, 'device') and term.device:
                                # Direct device connection
                                term_info['device_id'] = term.device.id
                                term_info['device_name'] = term.device.name
                                term_info['in_our_devices'] = term.device.id in device_ids
                            
                            cable_detail['a_terminations'].append(term_info)
                    except Exception as e:
                        cable_detail['a_terminations_error'] = str(e)
                    
                    # Analyze B terminations in detail
                    try:
                        b_terms = list(cable.b_terminations.all())
                        cable_detail['b_terminations_count'] = len(b_terms)
                        for term in b_terms[:2]:  # First 2 terminations
                            term_info = {
                                'term_type': type(term).__name__,
                                'has_termination': hasattr(term, 'termination'),
                            }
                            
                            # Check multiple ways to access the device
                            if hasattr(term, 'termination') and term.termination:
                                term_info['termination_type'] = type(term.termination).__name__
                                if hasattr(term.termination, 'device') and term.termination.device:
                                    term_info['device_id'] = term.termination.device.id
                                    term_info['device_name'] = term.termination.device.name
                                    term_info['interface_name'] = getattr(term.termination, 'name', 'No Name')
                                    term_info['in_our_devices'] = term.termination.device.id in device_ids
                            elif hasattr(term, 'device') and term.device:
                                # Direct device connection
                                term_info['device_id'] = term.device.id
                                term_info['device_name'] = term.device.name
                                term_info['in_our_devices'] = term.device.id in device_ids
                                
                            cable_detail['b_terminations'].append(term_info)
                    except Exception as e:
                        cable_detail['b_terminations_error'] = str(e)
                    
                    debug_info['cable_details'].append(cable_detail)
                
                # Filter cables that connect our devices with improved logic
                device_connected_cables = []
                for cable in all_cables:
                    a_device_connected = False
                    b_device_connected = False
                    
                    # Check A terminations - try multiple NetBox v4+ structures
                    try:
                        for termination in cable.a_terminations.all():
                            # Method 1: termination.termination.device (newer NetBox)
                            if (hasattr(termination, 'termination') and 
                                hasattr(termination.termination, 'device') and
                                termination.termination.device.id in device_ids):
                                a_device_connected = True
                                break
                            # Method 2: termination.device (direct device connection)
                            elif (hasattr(termination, 'device') and 
                                  termination.device.id in device_ids):
                                a_device_connected = True
                                break
                            # Method 3: Check if termination is an interface with device
                            elif (hasattr(termination, 'id') and hasattr(termination, 'device') and
                                  termination.device.id in device_ids):
                                a_device_connected = True
                                break
                    except Exception as e:
                        debug_info['a_termination_errors'] = debug_info.get('a_termination_errors', [])
                        debug_info['a_termination_errors'].append(f"Cable {cable.id}: {str(e)}")
                    
                    # Check B terminations - try multiple structures
                    try:
                        for termination in cable.b_terminations.all():
                            # Method 1: termination.termination.device (newer NetBox)
                            if (hasattr(termination, 'termination') and 
                                hasattr(termination.termination, 'device') and
                                termination.termination.device.id in device_ids):
                                b_device_connected = True
                                break
                            # Method 2: termination.device (direct device connection)
                            elif (hasattr(termination, 'device') and 
                                  termination.device.id in device_ids):
                                b_device_connected = True
                                break
                            # Method 3: Check if termination is an interface with device
                            elif (hasattr(termination, 'id') and hasattr(termination, 'device') and
                                  termination.device.id in device_ids):
                                b_device_connected = True
                                break
                    except Exception as e:
                        debug_info['b_termination_errors'] = debug_info.get('b_termination_errors', [])
                        debug_info['b_termination_errors'].append(f"Cable {cable.id}: {str(e)}")
                    
                    # Add cable if it connects our devices
                    if a_device_connected and b_device_connected:
                        device_connected_cables.append(cable)
                        device_connected_cables.append(cable)
                
                cables = device_connected_cables
                connections_debug['device_connections'] = len(cables)
                connections_debug['method_used'] = 'cable_terminations'
                
                # Method 2: If no device connections, look for circuit connections
                if not cables:
                    from circuits.models import Circuit, CircuitTermination
                    
                    # Find circuits connected to our sites
                    site_ids = [d.site.id for d in devices if d.site]
                    circuit_terminations = CircuitTermination.objects.filter(
                        site_id__in=site_ids
                    ).select_related('circuit', 'site')
                    
                    # Group by circuit to find connections between sites
                    circuit_connections = {}
                    for termination in circuit_terminations:
                        circuit_id = termination.circuit.id
                        if circuit_id not in circuit_connections:
                            circuit_connections[circuit_id] = {
                                'circuit': termination.circuit,
                                'terminations': []
                            }
                        circuit_connections[circuit_id]['terminations'].append(termination)
                    
                    # Convert circuit connections to cable-like objects for visualization
                    for circuit_id, data in circuit_connections.items():
                        if len(data['terminations']) >= 2:
                            # Create a pseudo-cable for visualization
                            connections_debug['circuit_connections'] += 1
                    
                    connections_debug['method_used'] = 'circuits'
                
                debug_info.update(connections_debug)
                
            except Exception as e:
                debug_info['cable_error'] = str(e)
                cables = []
            
            # Group devices by site with enhanced organization
            sites_data = {}
            devices_processed = 0
            
            for device in devices:
                try:
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
                    devices_processed += 1
                    
                except Exception as e:
                    debug_info['device_processing_errors'] = debug_info.get('device_processing_errors', [])
                    debug_info['device_processing_errors'].append(f"Device {device.id}: {str(e)}")
                    continue
            
            debug_info['devices_processed'] = devices_processed
            debug_info['sites_created'] = len(sites_data)
            
            # Enhanced connection processing - ONLY use real NetBox connections
            connections = []
            real_connections = 0
            
            # Process physical cables ONLY
            for cable in cables:
                try:
                    connection = self._process_cable_connection(cable, device_ids)
                    if connection:
                        connections.append(connection)
                        real_connections += 1
                except Exception as e:
                    debug_info['connection_errors'] = debug_info.get('connection_errors', [])
                    debug_info['connection_errors'].append(f"Cable {cable.id}: {str(e)}")
                    continue
            
            debug_info['real_connections_found'] = real_connections
            debug_info['connection_sample'] = connections[:3] if connections else []
            debug_info['using_real_connections'] = real_connections > 0
            debug_info['mock_connections_disabled'] = True
            
            # Convert to list format
            sites_list = list(sites_data.values())
            all_devices = []
            for site in sites_list:
                all_devices.extend(site['devices'])
            
            debug_info['final_device_count'] = len(all_devices)
            debug_info['final_site_count'] = len(sites_list)
            debug_info['final_connection_count'] = len(connections)
            
            return {
                'devices': all_devices,
                'sites': sites_list,
                'connections': connections,
                'stats': {
                    'total_devices': len(all_devices),
                    'total_sites': len(sites_list),
                    'total_connections': len(connections)
                },
                'debug': debug_info  # Include debug info in response
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
            
            # Handle A terminations - try multiple NetBox structures
            if hasattr(cable, 'a_terminations'):
                for termination in cable.a_terminations.all():
                    # Method 1: termination.termination.device (CableTermination -> Interface -> Device)
                    if (hasattr(termination, 'termination') and 
                        hasattr(termination.termination, 'device') and
                        termination.termination.device.id in device_ids):
                        a_device_id = termination.termination.device.id
                        a_interface = termination.termination.name
                        break
                    # Method 2: termination.device (direct device connection)
                    elif (hasattr(termination, 'device') and 
                          termination.device.id in device_ids):
                        a_device_id = termination.device.id
                        a_interface = termination.name if hasattr(termination, 'name') else str(termination)
                        break
                    # Method 3: termination is an interface object directly
                    elif (hasattr(termination, 'id') and hasattr(termination, 'device') and
                          termination.device.id in device_ids):
                        a_device_id = termination.device.id
                        a_interface = termination.name
                        break
            
            # Handle B terminations - try multiple structures
            if hasattr(cable, 'b_terminations'):
                for termination in cable.b_terminations.all():
                    # Method 1: termination.termination.device (CableTermination -> Interface -> Device)
                    if (hasattr(termination, 'termination') and 
                        hasattr(termination.termination, 'device') and
                        termination.termination.device.id in device_ids):
                        b_device_id = termination.termination.device.id
                        b_interface = termination.termination.name
                        break
                    # Method 2: termination.device (direct device connection)
                    elif (hasattr(termination, 'device') and 
                          termination.device.id in device_ids):
                        b_device_id = termination.device.id
                        b_interface = termination.name if hasattr(termination, 'name') else str(termination)
                        break
                    # Method 3: termination is an interface object directly
                    elif (hasattr(termination, 'id') and hasattr(termination, 'device') and
                          termination.device.id in device_ids):
                        b_device_id = termination.device.id
                        b_interface = termination.name
                        break
            
            # Return connection if both ends found and they're different devices
            if a_device_id and b_device_id and a_device_id != b_device_id:
                return {
                    'id': cable.id,
                    'source': a_device_id,
                    'target': b_device_id,
                    'type': str(cable.type) if cable.type else 'ethernet',
                    'status': str(cable.status) if cable.status else 'connected',
                    'length': float(cable.length) if cable.length else None,
                    'a_interface': a_interface,
                    'b_interface': b_interface,
                    'logical': False  # Mark as real connection
                }
            
            return None
            
        except Exception as e:
            print(f"Cable processing error for cable {cable.id}: {e}")
            return None
    
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
    
    def _create_logical_connections(self, sites_data, device_ids):
        """Create logical connections for demo purposes when no physical cables exist"""
        connections = []
        connection_id = 10000  # Start with high ID to avoid conflicts
        
        try:
            for site_name, site_data in sites_data.items():
                site_devices = site_data['devices']
                
                # Group devices by type
                routers = [d for d in site_devices if d['type'] == 'router']
                switches = [d for d in site_devices if d['type'] == 'switch']
                firewalls = [d for d in site_devices if d['type'] == 'firewall']
                servers = [d for d in site_devices if d['type'] == 'server']
                aps = [d for d in site_devices if d['type'] == 'ap']
                
                # Connect routers to switches
                for router in routers:
                    for switch in switches[:2]:  # Connect to first 2 switches
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': router['id'],
                            'target': switch['id'],
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_interface': 'eth0',
                            'b_interface': 'eth0',
                            'logical': True
                        })
                        connection_id += 1
                
                # Connect switches to each other (create a mesh)
                for i, switch_a in enumerate(switches):
                    for switch_b in switches[i+1:i+3]:  # Connect to next 2 switches
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': switch_a['id'],
                            'target': switch_b['id'], 
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_interface': 'eth1',
                            'b_interface': 'eth1',
                            'logical': True
                        })
                        connection_id += 1
                
                # Connect switches to servers and APs
                for i, switch in enumerate(switches):
                    # Connect to servers
                    for server in servers[i*2:(i+1)*2]:  # 2 servers per switch
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': switch['id'],
                            'target': server['id'],
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_interface': f'eth{i+10}',
                            'b_interface': 'eth0',
                            'logical': True
                        })
                        connection_id += 1
                    
                    # Connect to APs
                    for ap in aps[i*1:(i+1)*1]:  # 1 AP per switch
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': switch['id'],
                            'target': ap['id'],
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_interface': f'eth{i+20}',
                            'b_interface': 'eth0',
                            'logical': True
                        })
                        connection_id += 1
                
                # Connect firewalls to routers
                for firewall in firewalls:
                    for router in routers[:1]:  # Connect to first router
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': firewall['id'],
                            'target': router['id'],
                            'type': 'ethernet',
                            'status': 'connected',
                            'length': None,
                            'a_interface': 'eth0',
                            'b_interface': 'eth1',
                            'logical': True
                        })
                        connection_id += 1
            
            # Inter-site connections (connect routers from different sites)
            all_sites = list(sites_data.values())
            for i, site_a in enumerate(all_sites):
                for site_b in all_sites[i+1:]:
                    routers_a = [d for d in site_a['devices'] if d['type'] == 'router']
                    routers_b = [d for d in site_b['devices'] if d['type'] == 'router']
                    
                    if routers_a and routers_b:
                        connections.append({
                            'id': f'logical-{connection_id}',
                            'source': routers_a[0]['id'],
                            'target': routers_b[0]['id'],
                            'type': 'wan',
                            'status': 'connected',
                            'length': 100,
                            'a_interface': 'wan0',
                            'b_interface': 'wan0',
                            'logical': True,
                            'inter_site': True
                        })
                        connection_id += 1
                        
        except Exception as e:
            print(f"Error creating logical connections: {e}")
        
        return connections


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
