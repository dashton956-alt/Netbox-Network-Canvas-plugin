#!/usr/bin/env python3
"""
Comprehensive NetBox Network Data Population Script
Populates NetBox with Layer 2 and Layer 3 infrastructure including:
- Enterprise network hierarchy (sites, racks, devices)
- Cables and connections
- Wireless infrastructure
- VLANs and IP addressing
- Complete network topology for testing the plugin
"""

import os
import sys
import django
from django.db import transaction

# Setup Django environment
sys.path.insert(0, '/opt/netbox/netbox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
django.setup()

from dcim.models import (
    Site, Manufacturer, DeviceType, DeviceRole, Device, Platform,
    Interface, Cable, CableTermination, Rack, RackRole, Location
)
from ipam.models import VRF, VLAN, VLANGroup, Prefix, IPAddress, Role as IPRole
from wireless.models import WirelessLAN, WirelessLANGroup
from tenancy.models import Tenant
from vpn.models import Tunnel, TunnelGroup, TunnelTermination

def create_manufacturers():
    """Create network equipment manufacturers"""
    manufacturers = [
        'Cisco', 'Juniper', 'HPE', 'Dell', 'Arista', 'Fortinet', 
        'Palo Alto', 'Ubiquiti', 'Meraki', 'Ruckus', 'Extreme',
        'VMware', 'Supermicro', 'F5'
    ]
    
    manufacturer_objects = []
    for name in manufacturers:
        manufacturer, created = Manufacturer.objects.get_or_create(
            name=name,
            defaults={'slug': name.lower().replace(' ', '-')}
        )
        manufacturer_objects.append(manufacturer)
        if created:
            print(f"Created manufacturer: {name}")
    
    return {m.name: m for m in manufacturer_objects}

def create_device_roles():
    """Create comprehensive device roles"""
    roles_data = [
        ('Core Switch', 'core-switch', 'ff0000'),  # Red
        ('Distribution Switch', 'dist-switch', 'ff8000'),  # Orange
        ('Access Switch', 'access-switch', 'ffff00'),  # Yellow
        ('Router', 'router', '0080ff'),  # Blue
        ('Firewall', 'firewall', 'ff0080'),  # Pink
        ('Load Balancer', 'load-balancer', '8000ff'),  # Purple
        ('Wireless Controller', 'wireless-controller', '00ff80'),  # Green
        ('Access Point', 'access-point', '80ff00'),  # Light Green
        ('Server', 'server', '00ffff'),  # Cyan
        ('Storage', 'storage', 'ff8080'),  # Light Red
        ('Hypervisor', 'hypervisor', '8080ff'),  # Light Blue
        ('Management', 'management', '808080'),  # Gray
        ('VPN Gateway', 'vpn-gateway', 'ff00ff'),  # Magenta
    ]
    
    role_objects = []
    for name, slug, color in roles_data:
        role, created = DeviceRole.objects.get_or_create(
            name=name,
            defaults={'slug': slug, 'color': color}
        )
        role_objects.append(role)
        if created:
            print(f"Created device role: {name}")
    
    return {r.name: r for r in role_objects}

def create_device_types(manufacturers):
    """Create comprehensive device types"""
    device_types_data = [
        # Cisco Switches
        ('Cisco', 'Catalyst 9500-48Y4C', 'catalyst-9500-48y4c', 'Core Switch', 52),
        ('Cisco', 'Catalyst 9400-SUP-1', 'catalyst-9400-sup-1', 'Distribution Switch', 48),
        ('Cisco', 'Catalyst 9200-48T', 'catalyst-9200-48t', 'Access Switch', 48),
        ('Cisco', 'Catalyst 9130AX', 'catalyst-9130ax', 'Access Point', 2),
        
        # Cisco Routers
        ('Cisco', 'ISR 4451', 'isr-4451', 'Router', 4),
        ('Cisco', 'ASR 1001-X', 'asr-1001-x', 'Router', 6),
        
        # Cisco Security
        ('Cisco', 'ASA 5525-X', 'asa-5525-x', 'Firewall', 8),
        ('Cisco', 'WLC 9800-40', 'wlc-9800-40', 'Wireless Controller', 4),
        
        # HPE Switches
        ('HPE', 'Aruba 8325-48Y8C', 'aruba-8325-48y8c', 'Core Switch', 56),
        ('HPE', 'Aruba 6300M-24G', 'aruba-6300m-24g', 'Access Switch', 24),
        
        # Juniper
        ('Juniper', 'EX4650-48Y', 'ex4650-48y', 'Distribution Switch', 48),
        ('Juniper', 'SRX550', 'srx550', 'Firewall', 8),
        
        # Servers
        ('Dell', 'PowerEdge R750', 'poweredge-r750', 'Server', 4),
        ('HPE', 'ProLiant DL380 Gen10', 'proliant-dl380-gen10', 'Server', 4),
        ('Supermicro', 'SuperServer 2049P', 'superserver-2049p', 'Hypervisor', 4),
        
        # Wireless
        ('Ubiquiti', 'UniFi AP AC Pro', 'unifi-ap-ac-pro', 'Access Point', 2),
        ('Ruckus', 'R750', 'ruckus-r750', 'Access Point', 2),
        
        # Load Balancers
        ('F5', 'BIG-IP 2600', 'big-ip-2600', 'Load Balancer', 8),
        
        # VPN Gateways
        ('Cisco', 'ASA 5516-X', 'asa-5516-x', 'VPN Gateway', 6),
        ('Fortinet', 'FortiGate 100F', 'fortigate-100f', 'VPN Gateway', 8),
        ('Palo Alto', 'PA-220', 'pa-220', 'VPN Gateway', 4),
        
        # Storage
        ('Dell', 'PowerVault ME4024', 'powervault-me4024', 'Storage', 4),
    ]
    
    device_type_objects = []
    roles = create_device_roles()
    
    for manufacturer_name, model, slug, role_name, port_count in device_types_data:
        manufacturer = manufacturers[manufacturer_name]
        role = roles[role_name]
        
        device_type, created = DeviceType.objects.get_or_create(
            manufacturer=manufacturer,
            model=model,
            defaults={
                'slug': slug,
                'part_number': f"PN-{slug.upper()}",
                'u_height': 1,
                'is_full_depth': True,
            }
        )
        device_type_objects.append((device_type, role, port_count))
        if created:
            print(f"Created device type: {manufacturer_name} {model}")
    
    return device_type_objects

def create_sites_and_locations():
    """Create enterprise sites and locations"""
    sites_data = [
        ('Headquarters', 'hq', 'New York, NY'),
        ('Branch Office East', 'branch-east', 'Boston, MA'),
        ('Branch Office West', 'branch-west', 'San Francisco, CA'),
        ('Data Center Primary', 'dc-primary', 'Dallas, TX'),
        ('Data Center DR', 'dc-dr', 'Chicago, IL'),
    ]
    
    site_objects = []
    for name, slug, address in sites_data:
        site, created = Site.objects.get_or_create(
            name=name,
            defaults={'slug': slug, 'physical_address': address}
        )
        site_objects.append(site)
        if created:
            print(f"Created site: {name}")
    
    # Create locations within sites
    locations_data = [
        ('Network Closet Floor 1', 'nc-floor-1', 'Headquarters'),
        ('Network Closet Floor 2', 'nc-floor-2', 'Headquarters'),
        ('Server Room', 'server-room', 'Headquarters'),
        ('Main IDF', 'main-idf', 'Branch Office East'),
        ('Main IDF', 'main-idf', 'Branch Office West'),
        ('Rack Row A', 'rack-row-a', 'Data Center Primary'),
        ('Rack Row B', 'rack-row-b', 'Data Center Primary'),
        ('Rack Row A', 'rack-row-a', 'Data Center DR'),
    ]
    
    location_objects = []
    site_dict = {s.name: s for s in site_objects}
    
    for name, slug, site_name in locations_data:
        site = site_dict[site_name]
        location, created = Location.objects.get_or_create(
            name=name,
            site=site,
            defaults={'slug': f"{site.slug}-{slug}"}
        )
        location_objects.append(location)
        if created:
            print(f"Created location: {name} at {site_name}")
    
    return site_objects, location_objects

def create_racks(sites, locations):
    """Create network racks"""
    rack_role, created = RackRole.objects.get_or_create(
        name='Network Equipment',
        defaults={'slug': 'network-equipment', 'color': '0066cc'}
    )
    
    racks_data = [
        ('Rack-HQ-01', 'Headquarters', 'Server Room'),
        ('Rack-HQ-02', 'Headquarters', 'Network Closet Floor 1'),
        ('Rack-HQ-03', 'Headquarters', 'Network Closet Floor 2'),
        ('Rack-BE-01', 'Branch Office East', 'Main IDF'),
        ('Rack-BW-01', 'Branch Office West', 'Main IDF'),
        ('Rack-DC1-A01', 'Data Center Primary', 'Rack Row A'),
        ('Rack-DC1-A02', 'Data Center Primary', 'Rack Row A'),
        ('Rack-DC1-B01', 'Data Center Primary', 'Rack Row B'),
        ('Rack-DC2-A01', 'Data Center DR', 'Rack Row A'),
    ]
    
    rack_objects = []
    site_dict = {s.name: s for s in sites}
    location_dict = {f"{l.site.name}|{l.name}": l for l in locations}
    
    for name, site_name, location_name in racks_data:
        site = site_dict[site_name]
        location = location_dict.get(f"{site_name}|{location_name}")
        
        rack, created = Rack.objects.get_or_create(
            name=name,
            site=site,
            defaults={
                'location': location,
                'role': rack_role,
                'u_height': 42,
                'width': 19,  # 19 inch
            }
        )
        rack_objects.append(rack)
        if created:
            print(f"Created rack: {name}")
    
    return rack_objects

def create_vlans_and_subnets():
    """Create VLANs and IP subnets"""
    # Create VLAN Groups
    vlan_groups_data = [
        ('Headquarters', 'hq'),
        ('Branch Offices', 'branches'),
        ('Data Centers', 'datacenters'),
        ('Wireless', 'wireless'),
        ('Management', 'management'),
    ]
    
    vlan_group_objects = []
    for name, slug in vlan_groups_data:
        vlan_group, created = VLANGroup.objects.get_or_create(
            name=name,
            defaults={'slug': slug}
        )
        vlan_group_objects.append(vlan_group)
        if created:
            print(f"Created VLAN group: {name}")
    
    vlan_group_dict = {vg.name: vg for vg in vlan_group_objects}
    
    # Create VLANs
    vlans_data = [
        # Management VLANs
        (1, 'Default', 'Management', None),
        (10, 'Management', 'Management', '10.1.10.0/24'),
        (20, 'Network Management', 'Management', '10.1.20.0/24'),
        
        # User VLANs - HQ
        (100, 'HQ-Users-Floor1', 'Headquarters', '10.1.100.0/24'),
        (101, 'HQ-Users-Floor2', 'Headquarters', '10.1.101.0/24'),
        (110, 'HQ-Servers', 'Headquarters', '10.1.110.0/24'),
        (120, 'HQ-DMZ', 'Headquarters', '10.1.120.0/24'),
        
        # Branch VLANs
        (200, 'Branch-East-Users', 'Branch Offices', '10.2.200.0/24'),
        (201, 'Branch-East-Printers', 'Branch Offices', '10.2.201.0/24'),
        (210, 'Branch-West-Users', 'Branch Offices', '10.2.210.0/24'),
        (211, 'Branch-West-Printers', 'Branch Offices', '10.2.211.0/24'),
        
        # Data Center VLANs
        (300, 'DC-Web-Servers', 'Data Centers', '10.3.100.0/24'),
        (301, 'DC-App-Servers', 'Data Centers', '10.3.101.0/24'),
        (302, 'DC-DB-Servers', 'Data Centers', '10.3.102.0/24'),
        (310, 'DC-Storage', 'Data Centers', '10.3.110.0/24'),
        (320, 'DC-Backup', 'Data Centers', '10.3.120.0/24'),
        
        # Wireless VLANs
        (400, 'WiFi-Corporate', 'Wireless', '10.4.100.0/24'),
        (401, 'WiFi-Guest', 'Wireless', '10.4.101.0/24'),
        (410, 'WiFi-IoT', 'Wireless', '10.4.110.0/24'),
    ]
    
    vlan_objects = []
    for vid, name, group_name, subnet in vlans_data:
        group = vlan_group_dict[group_name]
        vlan, created = VLAN.objects.get_or_create(
            vid=vid,
            name=name,
            group=group,
        )
        vlan_objects.append((vlan, subnet))
        if created:
            print(f"Created VLAN {vid}: {name}")
    
    # Create IP Prefixes
    prefix_objects = []
    for vlan, subnet in vlan_objects:
        if subnet:
            prefix, created = Prefix.objects.get_or_create(
                prefix=subnet,
                defaults={
                    'vlan': vlan,
                    'description': f"Subnet for VLAN {vlan.vid} - {vlan.name}",
                    'status': 'active',
                }
            )
            prefix_objects.append(prefix)
            if created:
                print(f"Created prefix: {subnet} for VLAN {vlan.vid}")
    
    return vlan_objects, prefix_objects

def create_comprehensive_devices(device_type_objects, sites, racks):
    """Create a comprehensive network infrastructure"""
    site_dict = {s.name: s for s in sites}
    rack_dict = {r.name: r for r in racks}
    device_type_dict = {dt[0].model: dt for dt in device_type_objects}
    
    # Define network topology
    devices_data = [
        # Headquarters - Core Infrastructure
        ('HQ-CORE-SW-01', 'Catalyst 9500-48Y4C', 'Headquarters', 'Rack-HQ-01', 1, '10.1.10.10'),
        ('HQ-CORE-SW-02', 'Catalyst 9500-48Y4C', 'Headquarters', 'Rack-HQ-01', 2, '10.1.10.11'),
        ('HQ-DIST-SW-01', 'Catalyst 9400-SUP-1', 'Headquarters', 'Rack-HQ-02', 1, '10.1.10.20'),
        ('HQ-DIST-SW-02', 'Catalyst 9400-SUP-1', 'Headquarters', 'Rack-HQ-03', 1, '10.1.10.21'),
        
        # Headquarters - Access Layer
        ('HQ-ACC-SW-01', 'Catalyst 9200-48T', 'Headquarters', 'Rack-HQ-02', 2, '10.1.10.30'),
        ('HQ-ACC-SW-02', 'Catalyst 9200-48T', 'Headquarters', 'Rack-HQ-02', 3, '10.1.10.31'),
        ('HQ-ACC-SW-03', 'Catalyst 9200-48T', 'Headquarters', 'Rack-HQ-03', 2, '10.1.10.32'),
        ('HQ-ACC-SW-04', 'Catalyst 9200-48T', 'Headquarters', 'Rack-HQ-03', 3, '10.1.10.33'),
        
        # Headquarters - Routers and Firewalls
        ('HQ-RTR-01', 'ASR 1001-X', 'Headquarters', 'Rack-HQ-01', 3, '10.1.10.1'),
        ('HQ-RTR-02', 'ISR 4451', 'Headquarters', 'Rack-HQ-01', 4, '10.1.10.2'),
        ('HQ-FW-01', 'ASA 5525-X', 'Headquarters', 'Rack-HQ-01', 5, '10.1.10.5'),
        ('HQ-LB-01', 'BIG-IP 2600', 'Headquarters', 'Rack-HQ-01', 6, '10.1.10.50'),
        ('HQ-VPN-GW-01', 'ASA 5516-X', 'Headquarters', 'Rack-HQ-01', 8, '10.1.10.100'),
        
        # Headquarters - Wireless
        ('HQ-WLC-01', 'WLC 9800-40', 'Headquarters', 'Rack-HQ-01', 7, '10.1.10.60'),
        ('HQ-AP-01', 'Catalyst 9130AX', 'Headquarters', None, None, '10.4.100.10'),
        ('HQ-AP-02', 'UniFi AP AC Pro', 'Headquarters', None, None, '10.4.100.11'),
        ('HQ-AP-03', 'Ruckus R750', 'Headquarters', None, None, '10.4.100.12'),
        
        # Headquarters - Servers
        ('HQ-SRV-WEB-01', 'PowerEdge R750', 'Headquarters', 'Rack-HQ-01', 10, '10.1.110.10'),
        ('HQ-SRV-APP-01', 'ProLiant DL380 Gen10', 'Headquarters', 'Rack-HQ-01', 11, '10.1.110.11'),
        ('HQ-SRV-DB-01', 'PowerEdge R750', 'Headquarters', 'Rack-HQ-01', 12, '10.1.110.12'),
        ('HQ-HV-01', 'SuperServer 2049P', 'Headquarters', 'Rack-HQ-01', 15, '10.1.110.20'),
        ('HQ-SAN-01', 'PowerVault ME4024', 'Headquarters', 'Rack-HQ-01', 20, '10.3.110.10'),
        
        # Branch Office East
        ('BE-RTR-01', 'ISR 4451', 'Branch Office East', 'Rack-BE-01', 1, '10.2.10.1'),
        ('BE-SW-01', 'Aruba 6300M-24G', 'Branch Office East', 'Rack-BE-01', 2, '10.2.10.10'),
        ('BE-VPN-GW-01', 'FortiGate 100F', 'Branch Office East', 'Rack-BE-01', 3, '10.2.10.100'),
        ('BE-AP-01', 'UniFi AP AC Pro', 'Branch Office East', None, None, '10.4.100.20'),
        ('BE-AP-02', 'UniFi AP AC Pro', 'Branch Office East', None, None, '10.4.100.21'),
        
        # Branch Office West
        ('BW-RTR-01', 'ISR 4451', 'Branch Office West', 'Rack-BW-01', 1, '10.2.20.1'),
        ('BW-SW-01', 'Aruba 6300M-24G', 'Branch Office West', 'Rack-BW-01', 2, '10.2.20.10'),
        ('BW-VPN-GW-01', 'PA-220', 'Branch Office West', 'Rack-BW-01', 3, '10.2.20.100'),
        ('BW-AP-01', 'Ruckus R750', 'Branch Office West', None, None, '10.4.100.30'),
        ('BW-AP-02', 'Ruckus R750', 'Branch Office West', None, None, '10.4.100.31'),
        
        # Data Center Primary - Core
        ('DC1-CORE-SW-01', 'Aruba 8325-48Y8C', 'Data Center Primary', 'Rack-DC1-A01', 1, '10.3.10.10'),
        ('DC1-CORE-SW-02', 'Aruba 8325-48Y8C', 'Data Center Primary', 'Rack-DC1-A01', 2, '10.3.10.11'),
        ('DC1-FW-01', 'SRX550', 'Data Center Primary', 'Rack-DC1-A01', 3, '10.3.10.5'),
        ('DC1-VPN-GW-01', 'ASA 5516-X', 'Data Center Primary', 'Rack-DC1-A01', 4, '10.3.10.100'),
        
        # Data Center Primary - Servers
        ('DC1-SRV-WEB-01', 'PowerEdge R750', 'Data Center Primary', 'Rack-DC1-A02', 5, '10.3.100.10'),
        ('DC1-SRV-WEB-02', 'PowerEdge R750', 'Data Center Primary', 'Rack-DC1-A02', 6, '10.3.100.11'),
        ('DC1-SRV-APP-01', 'ProLiant DL380 Gen10', 'Data Center Primary', 'Rack-DC1-B01', 5, '10.3.101.10'),
        ('DC1-SRV-APP-02', 'ProLiant DL380 Gen10', 'Data Center Primary', 'Rack-DC1-B01', 6, '10.3.101.11'),
        ('DC1-SRV-DB-01', 'PowerEdge R750', 'Data Center Primary', 'Rack-DC1-B01', 10, '10.3.102.10'),
        ('DC1-HV-01', 'SuperServer 2049P', 'Data Center Primary', 'Rack-DC1-A02', 15, '10.3.110.30'),
        ('DC1-HV-02', 'SuperServer 2049P', 'Data Center Primary', 'Rack-DC1-A02', 16, '10.3.110.31'),
        
        # Data Center DR
        ('DC2-CORE-SW-01', 'EX4650-48Y', 'Data Center DR', 'Rack-DC2-A01', 1, '10.3.20.10'),
        ('DC2-FW-01', 'SRX550', 'Data Center DR', 'Rack-DC2-A01', 2, '10.3.20.5'),
        ('DC2-VPN-GW-01', 'FortiGate 100F', 'Data Center DR', 'Rack-DC2-A01', 3, '10.3.20.100'),
        ('DC2-SRV-DB-DR', 'PowerEdge R750', 'Data Center DR', 'Rack-DC2-A01', 10, '10.3.102.20'),
    ]
    
    device_objects = []
    
    with transaction.atomic():
        for device_name, model, site_name, rack_name, position, ip_addr in devices_data:
            if model not in device_type_dict:
                print(f"Warning: Device type '{model}' not found, skipping {device_name}")
                continue
                
            device_type_info = device_type_dict[model]
            device_type, role, port_count = device_type_info
            site = site_dict[site_name]
            rack = rack_dict[rack_name] if rack_name else None
            
            device, created = Device.objects.get_or_create(
                name=device_name,
                defaults={
                    'device_type': device_type,
                    'role': role,
                    'site': site,
                    'rack': rack,
                    'position': position,
                    'status': 'active',
                }
            )
            
            if created:
                print(f"Created device: {device_name}")
                
                # Create management interface and IP
                mgmt_interface, created = Interface.objects.get_or_create(
                    device=device,
                    name='Management',
                    defaults={
                        'type': '1000base-t',
                        'mgmt_only': True,
                    }
                )
                
                if created and ip_addr:
                    ip_address, created = IPAddress.objects.get_or_create(
                        address=f"{ip_addr}/24",
                        defaults={'status': 'active'}
                    )
                    if created:
                        mgmt_interface.ip_addresses.add(ip_address)
                        device.primary_ip4 = ip_address
                        device.save()
                
                # Create network interfaces based on device type
                create_device_interfaces(device, port_count)
            
            device_objects.append(device)
    
    return device_objects

def create_device_interfaces(device, port_count):
    """Create network interfaces for devices"""
    interface_types = {
        'Switch': '1000base-t',
        'Router': '1000base-t', 
        'Firewall': '1000base-t',
        'Server': '1000base-t',
        'Access Point': '1000base-t',
        'Wireless Controller': '1000base-t',
        'Load Balancer': '1000base-t',
        'Storage': '1000base-t',
    }
    
    # Determine interface naming convention
    if 'Switch' in device.role.name or 'AP' in device.name:
        interface_prefix = 'GigabitEthernet'
        interface_format = lambda i: f"{interface_prefix}1/0/{i+1}"
    elif 'Router' in device.role.name:
        interface_prefix = 'GigabitEthernet'
        interface_format = lambda i: f"{interface_prefix}0/0/{i}"
    else:
        interface_prefix = 'eth'
        interface_format = lambda i: f"{interface_prefix}{i}"
    
    interface_type = interface_types.get(device.role.name, '1000base-t')
    
    # Create interfaces
    for i in range(port_count):
        interface_name = interface_format(i)
        
        Interface.objects.get_or_create(
            device=device,
            name=interface_name,
            defaults={
                'type': interface_type,
                'enabled': True,
            }
        )

def create_network_cables(devices):
    """Create comprehensive cable connections"""
    device_dict = {d.name: d for d in devices}
    
    # Define cable connections (source_device, source_interface, target_device, target_interface)
    cable_connections = [
        # Core to Distribution connections
        ('HQ-CORE-SW-01', 'GigabitEthernet1/0/1', 'HQ-DIST-SW-01', 'GigabitEthernet1/0/1'),
        ('HQ-CORE-SW-01', 'GigabitEthernet1/0/2', 'HQ-DIST-SW-02', 'GigabitEthernet1/0/1'),
        ('HQ-CORE-SW-02', 'GigabitEthernet1/0/1', 'HQ-DIST-SW-01', 'GigabitEthernet1/0/2'),
        ('HQ-CORE-SW-02', 'GigabitEthernet1/0/2', 'HQ-DIST-SW-02', 'GigabitEthernet1/0/2'),
        
        # Core redundancy
        ('HQ-CORE-SW-01', 'GigabitEthernet1/0/47', 'HQ-CORE-SW-02', 'GigabitEthernet1/0/47'),
        ('HQ-CORE-SW-01', 'GigabitEthernet1/0/48', 'HQ-CORE-SW-02', 'GigabitEthernet1/0/48'),
        
        # Distribution to Access connections
        ('HQ-DIST-SW-01', 'GigabitEthernet1/0/10', 'HQ-ACC-SW-01', 'GigabitEthernet1/0/47'),
        ('HQ-DIST-SW-01', 'GigabitEthernet1/0/11', 'HQ-ACC-SW-02', 'GigabitEthernet1/0/47'),
        ('HQ-DIST-SW-02', 'GigabitEthernet1/0/10', 'HQ-ACC-SW-03', 'GigabitEthernet1/0/47'),
        ('HQ-DIST-SW-02', 'GigabitEthernet1/0/11', 'HQ-ACC-SW-04', 'GigabitEthernet1/0/47'),
        
        # Access switch redundancy
        ('HQ-DIST-SW-02', 'GigabitEthernet1/0/12', 'HQ-ACC-SW-01', 'GigabitEthernet1/0/48'),
        ('HQ-DIST-SW-01', 'GigabitEthernet1/0/12', 'HQ-ACC-SW-02', 'GigabitEthernet1/0/48'),
        
        # Router connections
        ('HQ-RTR-01', 'GigabitEthernet0/0/0', 'HQ-CORE-SW-01', 'GigabitEthernet1/0/45'),
        ('HQ-RTR-02', 'GigabitEthernet0/0/0', 'HQ-CORE-SW-02', 'GigabitEthernet1/0/45'),
        
        # Firewall connections
        ('HQ-FW-01', 'GigabitEthernet1/0/1', 'HQ-CORE-SW-01', 'GigabitEthernet1/0/46'),
        ('HQ-FW-01', 'GigabitEthernet1/0/2', 'HQ-RTR-01', 'GigabitEthernet0/0/1'),
        
        # Load Balancer
        ('HQ-LB-01', 'eth0', 'HQ-CORE-SW-01', 'GigabitEthernet1/0/40'),
        ('HQ-LB-01', 'eth1', 'HQ-CORE-SW-02', 'GigabitEthernet1/0/40'),
        
        # Wireless Controller
        ('HQ-WLC-01', 'eth0', 'HQ-CORE-SW-01', 'GigabitEthernet1/0/30'),
        
        # Server connections
        ('HQ-SRV-WEB-01', 'eth0', 'HQ-ACC-SW-01', 'GigabitEthernet1/0/10'),
        ('HQ-SRV-APP-01', 'eth0', 'HQ-ACC-SW-01', 'GigabitEthernet1/0/11'),
        ('HQ-SRV-DB-01', 'eth0', 'HQ-ACC-SW-01', 'GigabitEthernet1/0/12'),
        ('HQ-HV-01', 'eth0', 'HQ-ACC-SW-02', 'GigabitEthernet1/0/10'),
        ('HQ-SAN-01', 'eth0', 'HQ-ACC-SW-02', 'GigabitEthernet1/0/20'),
        
        # Branch Office East
        ('BE-RTR-01', 'GigabitEthernet0/0/0', 'BE-SW-01', 'GigabitEthernet1/0/24'),
        
        # Branch Office West  
        ('BW-RTR-01', 'GigabitEthernet0/0/0', 'BW-SW-01', 'GigabitEthernet1/0/24'),
        
        # Data Center Primary
        ('DC1-CORE-SW-01', 'GigabitEthernet1/0/1', 'DC1-CORE-SW-02', 'GigabitEthernet1/0/1'),
        ('DC1-FW-01', 'GigabitEthernet1/0/1', 'DC1-CORE-SW-01', 'GigabitEthernet1/0/45'),
        ('DC1-SRV-WEB-01', 'eth0', 'DC1-CORE-SW-01', 'GigabitEthernet1/0/10'),
        ('DC1-SRV-WEB-02', 'eth0', 'DC1-CORE-SW-02', 'GigabitEthernet1/0/10'),
        ('DC1-SRV-APP-01', 'eth0', 'DC1-CORE-SW-01', 'GigabitEthernet1/0/15'),
        ('DC1-SRV-APP-02', 'eth0', 'DC1-CORE-SW-02', 'GigabitEthernet1/0/15'),
        ('DC1-SRV-DB-01', 'eth0', 'DC1-CORE-SW-01', 'GigabitEthernet1/0/20'),
        ('DC1-HV-01', 'eth0', 'DC1-CORE-SW-01', 'GigabitEthernet1/0/25'),
        ('DC1-HV-02', 'eth0', 'DC1-CORE-SW-02', 'GigabitEthernet1/0/25'),
        
        # WAN connections (simulated with cables)
        ('HQ-RTR-01', 'GigabitEthernet0/0/2', 'BE-RTR-01', 'GigabitEthernet0/0/1'),
        ('HQ-RTR-02', 'GigabitEthernet0/0/2', 'BW-RTR-01', 'GigabitEthernet0/0/1'),
        ('HQ-RTR-01', 'GigabitEthernet0/0/3', 'DC1-FW-01', 'GigabitEthernet1/0/2'),
        ('HQ-RTR-02', 'GigabitEthernet0/0/3', 'DC2-FW-01', 'GigabitEthernet1/0/1'),
    ]
    
    cable_objects = []
    
    with transaction.atomic():
        for src_device_name, src_interface_name, dst_device_name, dst_interface_name in cable_connections:
            src_device = device_dict.get(src_device_name)
            dst_device = device_dict.get(dst_device_name)
            
            if not src_device or not dst_device:
                continue
            
            try:
                src_interface = Interface.objects.get(device=src_device, name=src_interface_name)
                dst_interface = Interface.objects.get(device=dst_device, name=dst_interface_name)
                
                # Create cable
                cable = Cable(
                    type='cat6',
                    status='connected',
                    length=1,
                    length_unit='m'
                )
                cable.save()
                
                # Add terminations
                CableTermination.objects.create(
                    cable=cable,
                    termination=src_interface
                )
                CableTermination.objects.create(
                    cable=cable,
                    termination=dst_interface
                )
                
                cable_objects.append(cable)
                print(f"Created cable: {src_device_name}:{src_interface_name} -> {dst_device_name}:{dst_interface_name}")
                
            except Interface.DoesNotExist as e:
                print(f"Interface not found: {e}")
                continue
            except Exception as e:
                print(f"Error creating cable: {e}")
                continue
    
    return cable_objects

def create_wireless_infrastructure():
    """Create wireless LANs and groups"""
    # Create Wireless LAN Groups
    wlan_groups_data = [
        ('Corporate', 'corporate'),
        ('Guest', 'guest'),
        ('IoT', 'iot'),
    ]
    
    wlan_group_objects = []
    for name, slug in wlan_groups_data:
        try:
            wlan_group, created = WirelessLANGroup.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            wlan_group_objects.append(wlan_group)
            if created:
                print(f"Created Wireless LAN group: {name}")
        except Exception as e:
            print(f"Wireless model not available: {e}")
            return []
    
    # Create Wireless LANs
    wlan_group_dict = {wg.name: wg for wg in wlan_group_objects}
    
    wlans_data = [
        ('Corp-WiFi', 'Corporate', 'WPA2-Enterprise', 'corp-wifi'),
        ('Guest-WiFi', 'Guest', 'WPA2-PSK', 'guest-wifi'),
        ('IoT-Devices', 'IoT', 'WPA2-PSK', 'iot-devices'),
    ]
    
    wlan_objects = []
    for ssid, group_name, auth, slug in wlans_data:
        try:
            group = wlan_group_dict[group_name]
            wlan, created = WirelessLAN.objects.get_or_create(
                ssid=ssid,
                defaults={
                    'group': group,
                    'auth_type': auth.lower().replace('-', '_'),
                }
            )
            wlan_objects.append(wlan)
            if created:
                print(f"Created Wireless LAN: {ssid}")
        except Exception as e:
            print(f"Error creating wireless LAN: {e}")
    
    return wlan_objects


def create_vpn_tunnels(devices):
    """Create VPN tunnels between sites"""
    print("Creating VPN tunnel groups...")
    
    # Create tunnel groups
    tunnel_groups = [
        ('Site-to-Site VPN', 'site-to-site-vpn', 'IPSec tunnels between sites'),
        ('Remote Access VPN', 'remote-access-vpn', 'Client VPN connections'),
    ]
    
    tunnel_group_objects = {}
    for name, slug, description in tunnel_groups:
        group, created = TunnelGroup.objects.get_or_create(
            name=name,
            defaults={'slug': slug, 'description': description}
        )
        tunnel_group_objects[name] = group
        if created:
            print(f"Created tunnel group: {name}")
    
    # Get VPN gateway devices
    device_dict = {d.name: d for d in devices}
    vpn_gateways = {
        'HQ-VPN-GW-01': device_dict.get('HQ-VPN-GW-01'),
        'BE-VPN-GW-01': device_dict.get('BE-VPN-GW-01'),
        'BW-VPN-GW-01': device_dict.get('BW-VPN-GW-01'),
        'DC1-VPN-GW-01': device_dict.get('DC1-VPN-GW-01'),
        'DC2-VPN-GW-01': device_dict.get('DC2-VPN-GW-01'),
    }
    
    # Filter out any None values (in case devices weren't created)
    vpn_gateways = {k: v for k, v in vpn_gateways.items() if v is not None}
    
    print("Creating site-to-site VPN tunnels...")
    
    # Define tunnel connections
    tunnel_connections = [
        # Site-to-site connections
        ('HQ-to-BE-Tunnel', 'HQ-VPN-GW-01', 'BE-VPN-GW-01', 'IPSEC_TRANSPORT', '10.1.10.100', '10.2.10.100'),
        ('HQ-to-BW-Tunnel', 'HQ-VPN-GW-01', 'BW-VPN-GW-01', 'IPSEC_TRANSPORT', '10.1.10.100', '10.2.20.100'),
        ('BE-to-BW-Tunnel', 'BE-VPN-GW-01', 'BW-VPN-GW-01', 'IPSEC_TRANSPORT', '10.2.10.100', '10.2.20.100'),
        
        # Data center connections  
        ('HQ-to-DC1-Tunnel', 'HQ-VPN-GW-01', 'DC1-VPN-GW-01', 'IPSEC_TRANSPORT', '10.1.10.100', '10.3.10.100'),
        ('HQ-to-DC2-Tunnel', 'HQ-VPN-GW-01', 'DC2-VPN-GW-01', 'IPSEC_TRANSPORT', '10.1.10.100', '10.3.20.100'),
        ('DC1-to-DC2-Tunnel', 'DC1-VPN-GW-01', 'DC2-VPN-GW-01', 'IPSEC_TRANSPORT', '10.3.10.100', '10.3.20.100'),
        
        # Branch to data center connections
        ('BE-to-DC1-Tunnel', 'BE-VPN-GW-01', 'DC1-VPN-GW-01', 'IPSEC_TRANSPORT', '10.2.10.100', '10.3.10.100'),
        ('BW-to-DC1-Tunnel', 'BW-VPN-GW-01', 'DC1-VPN-GW-01', 'IPSEC_TRANSPORT', '10.2.20.100', '10.3.10.100'),
    ]
    
    tunnel_objects = []
    tunnel_group = tunnel_group_objects['Site-to-Site VPN']
    
    with transaction.atomic():
        for tunnel_name, device_a_name, device_z_name, encapsulation, ip_a, ip_z in tunnel_connections:
            device_a = vpn_gateways.get(device_a_name)
            device_z = vpn_gateways.get(device_z_name)
            
            if not device_a or not device_z:
                print(f"Warning: Missing devices for tunnel {tunnel_name}, skipping")
                continue
            
            # Create tunnel
            tunnel, created = Tunnel.objects.get_or_create(
                name=tunnel_name,
                defaults={
                    'group': tunnel_group,
                    'encapsulation': encapsulation,
                    'description': f'Site-to-site VPN tunnel between {device_a.site.name} and {device_z.site.name}',
                    'status': 'active',
                }
            )
            tunnel_objects.append(tunnel)
            
            if created:
                print(f"Created tunnel: {tunnel_name}")
                
                # Create tunnel terminations (endpoints)
                try:
                    # Get or create interfaces for tunnel endpoints
                    interface_a, _ = Interface.objects.get_or_create(
                        device=device_a,
                        name=f'Tunnel{tunnel.pk}',
                        defaults={'type': 'virtual'}
                    )
                    
                    interface_z, _ = Interface.objects.get_or_create(
                        device=device_z,
                        name=f'Tunnel{tunnel.pk}',
                        defaults={'type': 'virtual'}
                    )
                    
                    # Create termination A
                    term_a, _ = TunnelTermination.objects.get_or_create(
                        tunnel=tunnel,
                        role='peer',
                        termination=interface_a,
                        defaults={'outside_ip': ip_a}
                    )
                    
                    # Create termination Z
                    term_z, _ = TunnelTermination.objects.get_or_create(
                        tunnel=tunnel,
                        role='peer',
                        termination=interface_z,
                        defaults={'outside_ip': ip_z}
                    )
                    
                except Exception as e:
                    print(f"Warning: Could not create tunnel terminations for {tunnel_name}: {e}")
    
    return tunnel_objects


def main():
    """Main function to populate comprehensive network data"""
    print("Starting comprehensive NetBox network population...")
    
    try:
        # Create base infrastructure
        print("\n=== Creating Manufacturers ===")
        manufacturers = create_manufacturers()
        
        print("\n=== Creating Device Types ===")
        device_types = create_device_types(manufacturers)
        
        print("\n=== Creating Sites and Locations ===")
        sites, locations = create_sites_and_locations()
        
        print("\n=== Creating Racks ===")
        racks = create_racks(sites, locations)
        
        print("\n=== Creating VLANs and Subnets ===")
        vlans, prefixes = create_vlans_and_subnets()
        
        print("\n=== Creating Devices ===")
        devices = create_comprehensive_devices(device_types, sites, racks)
        
        print("\n=== Creating Network Cables ===")
        cables = create_network_cables(devices)
        
        print("\n=== Creating Wireless Infrastructure ===")
        wireless_lans = create_wireless_infrastructure()
        
        print("\n=== Creating VPN Tunnels ===")
        vpn_tunnels = create_vpn_tunnels(devices)
        
        print(f"\n=== Population Complete ===")
        print(f"Created {len(devices)} devices")
        print(f"Created {len(cables)} cables")
        print(f"Created {len(vlans)} VLANs")
        print(f"Created {len(prefixes)} IP prefixes")
        print(f"Created {len(wireless_lans)} wireless LANs")
        print(f"Created {len(vpn_tunnels)} VPN tunnels")
        
        print("\nComprehensive network topology has been populated!")
        print("This includes:")
        print("- Multi-site enterprise network (HQ + 2 branches + 2 data centers)")
        print("- Layer 2/3 switching and routing")
        print("- Firewalls and load balancers")
        print("- VPN gateways with site-to-site tunnels")
        print("- Wireless infrastructure with APs and controllers")
        print("- Physical cable connections")
        print("- VLANs and IP addressing")
        print("- Server and storage infrastructure")
        print("\nYour NetBox Network Canvas plugin now has rich data to visualize!")
        
    except Exception as e:
        print(f"Error during population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
