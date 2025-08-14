#!/usr/bin/env python3
"""
Standalone script to populate NetBox with demo data.
Run this script from your NetBox installation directory.

Usage:
    cd /opt/netbox
    python /path/to/this/script/populate_demo_data.py
"""

import os
import sys
import django
import random

# Add NetBox to Python path and setup Django
netbox_path = '/opt/netbox/netbox'
if os.path.exists(netbox_path):
    sys.path.append(netbox_path)
else:
    # Try alternative path
    alt_path = '/opt/netbox'
    if os.path.exists(alt_path):
        sys.path.append(alt_path)
        netbox_path = alt_path
    else:
        print("NetBox not found. Please adjust the path in this script.")
        sys.exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Make sure you're running this from your NetBox installation directory:")
    print(f"cd {netbox_path} && python /path/to/this/script")
    sys.exit(1)

# Import NetBox models
from dcim.models import Site, Manufacturer, DeviceType, DeviceRole, Device, Interface, Cable
from django.db import transaction


def create_demo_data(sites=2, devices_per_site=10):
    """Create demo network topology data"""
    print(f"🚀 Creating demo data: {sites} sites with {devices_per_site} devices each...")
    
    with transaction.atomic():
        # Create manufacturers
        cisco, created = Manufacturer.objects.get_or_create(name='Cisco', defaults={'slug': 'cisco'})
        juniper, created = Manufacturer.objects.get_or_create(name='Juniper', defaults={'slug': 'juniper'})
        
        # Create device types
        switch_type, created = DeviceType.objects.get_or_create(
            manufacturer=cisco,
            model='Catalyst 9300',
            defaults={'slug': 'catalyst-9300', 'part_number': 'C9300-48P'}
        )
        router_type, created = DeviceType.objects.get_or_create(
            manufacturer=cisco,
            model='ISR 4331',
            defaults={'slug': 'isr-4331', 'part_number': 'ISR4331'}
        )
        
        # Create device roles
        switch_role, created = DeviceRole.objects.get_or_create(
            name='Switch',
            defaults={'slug': 'switch', 'color': '2196f3'}
        )
        router_role, created = DeviceRole.objects.get_or_create(
            name='Router',
            defaults={'slug': 'router', 'color': 'f44336'}
        )
        
        # Create sites and devices
        for site_num in range(1, sites + 1):
            site, created = Site.objects.get_or_create(
                name=f'Demo Site {site_num}',
                defaults={'slug': f'demo-site-{site_num}', 'status': 'active'}
            )
            
            # Create devices for this site
            for device_num in range(1, devices_per_site + 1):
                device_type = switch_type if device_num % 2 == 0 else router_type
                device_role = switch_role if device_num % 2 == 0 else router_role
                device_name = f'demo-{site.slug}-{device_num:02d}'
                
                device, created = Device.objects.get_or_create(
                    name=device_name,
                    site=site,
                    defaults={
                        'device_type': device_type,
                        'role': device_role,  # Changed from 'device_role' to 'role'
                        'status': 'active'
                    }
                )
                
                # Create interfaces for each device
                for int_num in range(1, 5):  # 4 interfaces per device
                    interface, created = Interface.objects.get_or_create(
                        device=device,
                        name=f'GigabitEthernet0/{int_num}',
                        defaults={'type': '1000base-t', 'enabled': True}
                    )
    
    print("✅ Demo data created successfully!")
    print(f"Created {sites} sites with {devices_per_site} devices each")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate NetBox with demo data')
    parser.add_argument('--sites', type=int, default=2, help='Number of sites')
    parser.add_argument('--devices-per-site', type=int, default=10, help='Devices per site')
    
    args = parser.parse_args()
    create_demo_data(sites=args.sites, devices_per_site=args.devices_per_site)
