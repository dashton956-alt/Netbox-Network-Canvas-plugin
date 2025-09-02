#!/usr/bin/env python3
"""
Quick NetBox data verification script
This script runs simple database queries to check NetBox data availability
"""

def test_netbox_data():
    """Test NetBox data availability without Django setup"""
    print("🔍 NetBox Data Quick Test")
    print("=" * 40)
    
    # Test if we can import NetBox models in this environment
    try:
        from dcim.models import Device, Site
        from ipam.models import VLAN
        from django.db.models import Count
        
        print("✅ NetBox models imported successfully")
        
        # Test basic queries
        total_devices = Device.objects.count()
        total_sites = Site.objects.count()
        total_vlans = VLAN.objects.count()
        
        print(f"📊 NetBox Database Contents:")
        print(f"   • Total Devices: {total_devices}")
        print(f"   • Total Sites: {total_sites}")
        print(f"   • Total VLANs: {total_vlans}")
        
        if total_devices == 0:
            print("\n❌ No devices found in NetBox!")
            print("💡 Run: python populate_demo_data.py")
            return False
        
        # Check device details
        print(f"\n🔍 Device Analysis:")
        devices_with_sites = Device.objects.exclude(site__isnull=True).count()
        devices_without_sites = total_devices - devices_with_sites
        
        print(f"   • Devices with sites: {devices_with_sites}")
        print(f"   • Devices without sites: {devices_without_sites}")
        
        # Check device statuses
        print(f"\n📋 Device Status Breakdown:")
        status_query = Device.objects.values('status').annotate(count=Count('id'))
        for item in status_query:
            print(f"   • {item['status']}: {item['count']} devices")
        
        # Check sites with devices
        print(f"\n🏢 Sites with Devices:")
        site_query = Device.objects.values('site__name').annotate(
            device_count=Count('id')
        ).exclude(site__isnull=True).order_by('-device_count')[:5]
        
        for item in site_query:
            print(f"   • {item['site__name']}: {item['device_count']} devices")
        
        # Sample devices
        print(f"\n📋 Sample Devices (first 5):")
        sample_devices = Device.objects.select_related(
            'site', 'device_type', 'role'
        )[:5]
        
        for device in sample_devices:
            site_name = device.site.name if device.site else 'No Site'
            device_type = device.device_type.model if device.device_type else 'No Type'
            role = device.role.name if device.role else 'No Role'
            
            print(f"   • ID:{device.id} '{device.name}' | Site: {site_name} | Type: {device_type} | Role: {role} | Status: {device.status}")
        
        print(f"\n✅ NetBox data looks good! The plugin should work.")
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import NetBox models: {e}")
        print("💡 This script must be run in NetBox environment")
        return False
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return False

if __name__ == "__main__":
    # Try to setup Django if possible
    try:
        import django
        import os
        import sys
        
        # Try to configure Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
        django.setup()
        print("✅ Django environment configured")
        
        test_netbox_data()
        
    except Exception as e:
        print(f"ℹ️ Cannot setup Django environment: {e}")
        print("💡 Run this script from NetBox directory with: python manage.py shell < script.py")
