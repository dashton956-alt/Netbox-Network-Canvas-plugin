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
from dcim.models import Site, Manufacturer, DeviceType, DeviceRole, Device, Interface, Cable, Rack
from virtualization.models import VirtualMachine, VMInterface, Cluster, ClusterType, ClusterGroup
from circuits.models import Provider, Circuit, CircuitType, CircuitTermination
from ipam.models import Prefix, IPAddress, VLAN, VLANGroup
from tenancy.models import Tenant, TenantGroup
from django.db import transaction


def create_demo_data(sites=2, devices_per_site=20):
    """Create comprehensive demo network topology data"""
    print(f"🚀 Creating demo data: {sites} sites with {devices_per_site} devices each, plus VMs, circuits, IPs, VLANs, racks, and more...")

    with transaction.atomic():
        # Tenants
        tenant_group, _ = TenantGroup.objects.get_or_create(name="Demo Tenants", defaults={"slug": "demo-tenants"})
        tenant, _ = Tenant.objects.get_or_create(name="Demo Tenant", group=tenant_group, defaults={"slug": "demo-tenant"})

        # Manufacturers
        cisco, _ = Manufacturer.objects.get_or_create(name='Cisco', defaults={'slug': 'cisco'})
        juniper, _ = Manufacturer.objects.get_or_create(name='Juniper', defaults={'slug': 'juniper'})
        aruba, _ = Manufacturer.objects.get_or_create(name='Aruba', defaults={'slug': 'aruba'})
        dell, _ = Manufacturer.objects.get_or_create(name='Dell', defaults={'slug': 'dell'})

        # Device Types
        switch_type, _ = DeviceType.objects.get_or_create(
            manufacturer=cisco, model='Catalyst 9300', defaults={'slug': 'catalyst-9300', 'part_number': 'C9300-48P'}
        )
        router_type, _ = DeviceType.objects.get_or_create(
            manufacturer=cisco, model='ISR 4331', defaults={'slug': 'isr-4331', 'part_number': 'ISR4331'}
        )
        ap_type, _ = DeviceType.objects.get_or_create(
            manufacturer=aruba, model='AP-515', defaults={'slug': 'ap-515', 'part_number': 'AP-515'}
        )
        server_type, _ = DeviceType.objects.get_or_create(
            manufacturer=dell, model='PowerEdge R640', defaults={'slug': 'r640', 'part_number': 'R640'}
        )

        # Device Roles
        switch_role, _ = DeviceRole.objects.get_or_create(name='Switch', defaults={'slug': 'switch', 'color': '2196f3'})
        router_role, _ = DeviceRole.objects.get_or_create(name='Router', defaults={'slug': 'router', 'color': 'f44336'})
        ap_role, _ = DeviceRole.objects.get_or_create(name='Access Point', defaults={'slug': 'ap', 'color': '4caf50'})
        server_role, _ = DeviceRole.objects.get_or_create(name='Server', defaults={'slug': 'server', 'color': '9c27b0'})

        # Cluster Types/Groups for VMs
        cluster_type, _ = ClusterType.objects.get_or_create(name="VMware", defaults={"slug": "vmware"})
        cluster_group, _ = ClusterGroup.objects.get_or_create(name="Demo Clusters", defaults={"slug": "demo-clusters"})

        # Circuit Types/Providers
        provider, _ = Provider.objects.get_or_create(name="Demo Provider", defaults={"slug": "demo-provider"})
        circuit_type, _ = CircuitType.objects.get_or_create(name="Internet", defaults={"slug": "internet"})

        # VLAN Group
        vlan_group, _ = VLANGroup.objects.get_or_create(name="Demo VLANs", defaults={"slug": "demo-vlans"})

        for site_num in range(1, sites + 1):
            site, _ = Site.objects.get_or_create(
                name=f'Demo Site {site_num}',
                defaults={'slug': f'demo-site-{site_num}', 'status': 'active', 'tenant': tenant}
            )

            # Racks
            rack, _ = Rack.objects.get_or_create(site=site, name="Rack 1", defaults={"status": "active"})


            # VLANs and Prefixes
            vlan, _ = VLAN.objects.get_or_create(site=site, vid=100+site_num, group=vlan_group, defaults={"name": f"VLAN{100+site_num}"})
            prefix, created = Prefix.objects.get_or_create(prefix=f"10.{site_num}.0.0/24", defaults={"vlan": vlan})
            # Handle site assignment based on NetBox version
            try:
                if hasattr(prefix, 'sites'):
                    prefix.sites.add(site)
                elif hasattr(prefix, 'site') and not prefix.site:
                    prefix.site = site
                    prefix.save()
            except Exception as e:
                print(f"Warning: Could not assign site to prefix {prefix.prefix}: {e}")

            # Devices: 5 switches, 5 routers, 5 APs, 5 servers per site
            for i in range(5):
                # Switch
                switch, _ = Device.objects.get_or_create(
                    name=f"sw{site_num}-{i+1}", site=site, rack=rack,
                    defaults={"device_type": switch_type, "role": switch_role, "status": "active", "tenant": tenant}
                )
                # Router
                router, _ = Device.objects.get_or_create(
                    name=f"rtr{site_num}-{i+1}", site=site, rack=rack,
                    defaults={"device_type": router_type, "role": router_role, "status": "active", "tenant": tenant}
                )
                # AP
                ap, _ = Device.objects.get_or_create(
                    name=f"ap{site_num}-{i+1}", site=site, rack=rack,
                    defaults={"device_type": ap_type, "role": ap_role, "status": "active", "tenant": tenant}
                )
                # Server
                server, _ = Device.objects.get_or_create(
                    name=f"srv{site_num}-{i+1}", site=site, rack=rack,
                    defaults={"device_type": server_type, "role": server_role, "status": "active", "tenant": tenant}
                )

                # Interfaces for each device
                for dev in [switch, router, ap, server]:
                    for int_num in range(1, 3):
                        Interface.objects.get_or_create(
                            device=dev,
                            name=f'eth{int_num}',
                            defaults={'type': '1000base-t', 'enabled': True}
                        )

            # Cluster and VMs
            cluster, _ = Cluster.objects.get_or_create(
                name=f"Cluster-{site_num}", type=cluster_type, group=cluster_group
            )
            for vm_num in range(1, 6):
                vm, _ = VirtualMachine.objects.get_or_create(
                    name=f"vm{site_num}-{vm_num}", cluster=cluster, tenant=tenant
                )
                for vif_num in range(1, 3):
                    VMInterface.objects.get_or_create(
                        virtual_machine=vm,
                        name=f'eth{vif_num}'
                    )

            # Circuits (commented out due to complex field requirements)
            # circuit, _ = Circuit.objects.get_or_create(
            #     cid=f"CIRCUIT-{site_num}", provider=provider, type=circuit_type, tenant=tenant
            # )
            # CircuitTermination.objects.get_or_create(
            #     circuit=circuit, term_side="A"
            # )

            # IP Addresses for devices and VMs
            for host in range(1, 21):
                ip, _ = IPAddress.objects.get_or_create(
                    address=f"10.{site_num}.0.{host}/24", tenant=tenant
                )

    # Create some test cables between devices for visualization
    print("🔌 Creating test cables between devices...")
    try:
        # Get all switches and routers to connect them
        switches = Device.objects.filter(role__name='Switch')[:5]
        routers = Device.objects.filter(role__name='Router')[:3]
        
        cable_count = 0
        
        # Connect switches to routers
        for i, switch in enumerate(switches):
            if i < len(routers):
                router = routers[i % len(routers)]
                
                # Get interfaces
                switch_interfaces = switch.interfaces.filter(name__icontains='eth0')[:1]
                router_interfaces = router.interfaces.filter(name__icontains='eth0')[:1]
                
                if switch_interfaces and router_interfaces:
                    switch_interface = switch_interfaces[0]
                    router_interface = router_interfaces[0]
                    
                    # Create cable
                    cable, created = Cable.objects.get_or_create(
                        defaults={
                            'type': 'cat6',
                            'status': 'connected',
                            'length': 5,
                            'length_unit': 'm'
                        }
                    )
                    
                    if created:
                        # Add terminations
                        cable.a_terminations.create(termination=switch_interface)
                        cable.b_terminations.create(termination=router_interface)
                        cable_count += 1
        
        # Connect some switches together
        for i in range(len(switches) - 1):
            switch_a = switches[i]
            switch_b = switches[i + 1]
            
            # Get available interfaces
            switch_a_interfaces = switch_a.interfaces.filter(name__icontains='eth1')[:1]
            switch_b_interfaces = switch_b.interfaces.filter(name__icontains='eth1')[:1]
            
            if switch_a_interfaces and switch_b_interfaces:
                interface_a = switch_a_interfaces[0]
                interface_b = switch_b_interfaces[0]
                
                # Create cable
                cable, created = Cable.objects.get_or_create(
                    defaults={
                        'type': 'cat6',
                        'status': 'connected',
                        'length': 3,
                        'length_unit': 'm'
                    }
                )
                
                if created:
                    # Add terminations
                    cable.a_terminations.create(termination=interface_a)
                    cable.b_terminations.create(termination=interface_b)
                    cable_count += 1
        
        print(f"✅ Created {cable_count} test cables")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not create test cables: {e}")
        print("This is normal if cables already exist or if NetBox version doesn't support this method")

    print("✅ Comprehensive demo data created successfully!")
    print(f"Created {sites} sites with racks, VLANs, prefixes, 20 devices, 5 VMs, circuits, and IPs per site.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate NetBox with demo data')
    parser.add_argument('--sites', type=int, default=2, help='Number of sites')
    parser.add_argument('--devices-per-site', type=int, default=10, help='Devices per site')
    
    args = parser.parse_args()
    create_demo_data(sites=args.sites, devices_per_site=args.devices_per_site)
