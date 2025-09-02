#!/usr/bin/env python3
"""
Script to clear NetBox demo data.
Run this script from your NetBox installation directory.

Usage:
    cd /opt/netbox
    python /path/to/this/script/clear_netbox_data.py

WARNING: This script will DELETE data from your NetBox database!
Use with caution and only on demo/test environments.
"""

import os
import sys
import django
import argparse

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


def clear_demo_data(confirm=False):
    """Clear demo data from NetBox"""
    
    if not confirm:
        print("⚠️  WARNING: This will DELETE data from your NetBox database!")
        print("This action is IRREVERSIBLE!")
        print()
        response = input("Are you sure you want to continue? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    print("🗑️  Starting to clear NetBox demo data...")
    
    try:
        with transaction.atomic():
            # Delete in reverse dependency order to avoid foreign key constraints
            
            # VM Interfaces
            vm_interfaces_count = VMInterface.objects.count()
            VMInterface.objects.all().delete()
            print(f"✅ Deleted {vm_interfaces_count} VM interfaces")
            
            # Virtual Machines
            vms_count = VirtualMachine.objects.count()
            VirtualMachine.objects.all().delete()
            print(f"✅ Deleted {vms_count} virtual machines")
            
            # Clusters
            clusters_count = Cluster.objects.count()
            Cluster.objects.all().delete()
            print(f"✅ Deleted {clusters_count} clusters")
            
            # Cluster Groups and Types
            cluster_groups_count = ClusterGroup.objects.count()
            ClusterGroup.objects.all().delete()
            print(f"✅ Deleted {cluster_groups_count} cluster groups")
            
            cluster_types_count = ClusterType.objects.count()
            ClusterType.objects.all().delete()
            print(f"✅ Deleted {cluster_types_count} cluster types")
            
            # Circuit Terminations
            circuit_terms_count = CircuitTermination.objects.count()
            CircuitTermination.objects.all().delete()
            print(f"✅ Deleted {circuit_terms_count} circuit terminations")
            
            # Circuits
            circuits_count = Circuit.objects.count()
            Circuit.objects.all().delete()
            print(f"✅ Deleted {circuits_count} circuits")
            
            # Circuit Types and Providers
            circuit_types_count = CircuitType.objects.count()
            CircuitType.objects.all().delete()
            print(f"✅ Deleted {circuit_types_count} circuit types")
            
            providers_count = Provider.objects.count()
            Provider.objects.all().delete()
            print(f"✅ Deleted {providers_count} providers")
            
            # IP Addresses
            ips_count = IPAddress.objects.count()
            IPAddress.objects.all().delete()
            print(f"✅ Deleted {ips_count} IP addresses")
            
            # Prefixes
            prefixes_count = Prefix.objects.count()
            Prefix.objects.all().delete()
            print(f"✅ Deleted {prefixes_count} prefixes")
            
            # VLANs
            vlans_count = VLAN.objects.count()
            VLAN.objects.all().delete()
            print(f"✅ Deleted {vlans_count} VLANs")
            
            # VLAN Groups
            vlan_groups_count = VLANGroup.objects.count()
            VLANGroup.objects.all().delete()
            print(f"✅ Deleted {vlan_groups_count} VLAN groups")
            
            # Cables
            cables_count = Cable.objects.count()
            Cable.objects.all().delete()
            print(f"✅ Deleted {cables_count} cables")
            
            # Interfaces
            interfaces_count = Interface.objects.count()
            Interface.objects.all().delete()
            print(f"✅ Deleted {interfaces_count} interfaces")
            
            # Devices
            devices_count = Device.objects.count()
            Device.objects.all().delete()
            print(f"✅ Deleted {devices_count} devices")
            
            # Racks
            racks_count = Rack.objects.count()
            Rack.objects.all().delete()
            print(f"✅ Deleted {racks_count} racks")
            
            # Device Types and Roles
            device_types_count = DeviceType.objects.count()
            DeviceType.objects.all().delete()
            print(f"✅ Deleted {device_types_count} device types")
            
            device_roles_count = DeviceRole.objects.count()
            DeviceRole.objects.all().delete()
            print(f"✅ Deleted {device_roles_count} device roles")
            
            # Manufacturers
            manufacturers_count = Manufacturer.objects.count()
            Manufacturer.objects.all().delete()
            print(f"✅ Deleted {manufacturers_count} manufacturers")
            
            # Sites
            sites_count = Site.objects.count()
            Site.objects.all().delete()
            print(f"✅ Deleted {sites_count} sites")
            
            # Tenants
            tenants_count = Tenant.objects.count()
            Tenant.objects.all().delete()
            print(f"✅ Deleted {tenants_count} tenants")
            
            # Tenant Groups
            tenant_groups_count = TenantGroup.objects.count()
            TenantGroup.objects.all().delete()
            print(f"✅ Deleted {tenant_groups_count} tenant groups")
            
        print()
        print("🎉 NetBox data cleared successfully!")
        print("Your NetBox database is now empty and ready for fresh data.")
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        print("Some data may have been partially deleted.")
        return False
    
    return True


def clear_demo_only():
    """Clear only demo-specific data (safer option)"""
    print("🗑️  Clearing demo-specific data only...")
    
    try:
        with transaction.atomic():
            # Delete demo sites and related data
            demo_sites = Site.objects.filter(name__startswith='Demo Site')
            demo_count = demo_sites.count()
            
            if demo_count == 0:
                print("No demo sites found.")
                return
            
            # This will cascade delete related objects
            demo_sites.delete()
            print(f"✅ Deleted {demo_count} demo sites and all related data")
            
            # Clean up demo tenants
            demo_tenants = Tenant.objects.filter(name__startswith='Demo')
            tenant_count = demo_tenants.count()
            demo_tenants.delete()
            print(f"✅ Deleted {tenant_count} demo tenants")
            
            # Clean up demo tenant groups
            demo_tenant_groups = TenantGroup.objects.filter(name__startswith='Demo')
            tenant_group_count = demo_tenant_groups.count()
            demo_tenant_groups.delete()
            print(f"✅ Deleted {tenant_group_count} demo tenant groups")
            
            # Clean up demo VLAN groups
            demo_vlan_groups = VLANGroup.objects.filter(name__startswith='Demo')
            vlan_group_count = demo_vlan_groups.count()
            demo_vlan_groups.delete()
            print(f"✅ Deleted {vlan_group_count} demo VLAN groups")
            
            # Clean up demo cluster groups
            demo_cluster_groups = ClusterGroup.objects.filter(name__startswith='Demo')
            cluster_group_count = demo_cluster_groups.count()
            demo_cluster_groups.delete()
            print(f"✅ Deleted {cluster_group_count} demo cluster groups")
            
        print()
        print("🎉 Demo data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing demo data: {e}")
        return False
    
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clear NetBox data')
    parser.add_argument('--all', action='store_true', help='Clear ALL data (dangerous!)')
    parser.add_argument('--demo-only', action='store_true', help='Clear only demo data (safer)')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.all:
        clear_demo_data(confirm=args.force)
    elif args.demo_only:
        clear_demo_only()
    else:
        print("Usage:")
        print("  --demo-only    Clear only demo data (recommended)")
        print("  --all          Clear ALL NetBox data (dangerous!)")
        print("  --force        Skip confirmation prompt")
        print()
        print("Example: python clear_netbox_data.py --demo-only")
