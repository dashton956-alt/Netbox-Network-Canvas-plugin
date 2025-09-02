#!/usr/bin/env python3
"""
Debug script to check NetBox device data for the enhanced plugin
"""

import django
import os
import sys

# Setup Django environment
sys.path.append('/opt/netbox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')

try:
    django.setup()
    print("✅ Django environment loaded successfully")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

try:
    from dcim.models import Device, Site, Cable
    from django.db.models import Count
    
    print("\n🔍 NETBOX DATA ANALYSIS")
    print("=" * 50)
    
    # Check total devices
    total_devices = Device.objects.count()
    print(f"📊 Total devices in NetBox: {total_devices}")
    
    if total_devices == 0:
        print("❌ No devices found in NetBox database")
        print("💡 You need to add some devices to NetBox first")
        sys.exit(1)
    
    # Check devices with sites
    devices_with_sites = Device.objects.exclude(site__isnull=True).count()
    print(f"🏢 Devices with sites assigned: {devices_with_sites}")
    
    # Check device statuses
    print("\n📋 Device Status Breakdown:")
    status_counts = {}
    for device in Device.objects.all():
        status = str(device.status)
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   • {status}: {count} devices")
    
    # Check sites
    sites_with_devices = Device.objects.values('site__name').annotate(
        device_count=Count('id')
    ).exclude(site__isnull=True).order_by('-device_count')
    
    print(f"\n🏗️ Sites with devices ({len(sites_with_devices)} sites):")
    for site_data in sites_with_devices[:10]:  # Show top 10
        print(f"   • {site_data['site__name']}: {site_data['device_count']} devices")
    
    # Check cables
    total_cables = Cable.objects.count()
    print(f"\n🔌 Total cables: {total_cables}")
    
    # Sample devices for debugging
    print(f"\n🔍 Sample devices (first 5):")
    for device in Device.objects.select_related('site', 'device_type', 'role')[:5]:
        print(f"   • ID:{device.id} '{device.name}' | Site: {device.site.name if device.site else 'None'} | Status: {device.status} | Type: {device.device_type.model if device.device_type else 'None'}")
    
    print(f"\n✅ NetBox appears to have data. The enhanced plugin should work!")
    print(f"🌐 Try accessing the Enhanced Dashboard in your NetBox web interface")
    
    # Test the plugin data method
    print(f"\n🧪 Testing enhanced plugin data method...")
    try:
        from netbox_network_canvas_plugin.views import EnhancedDashboardView
        view = EnhancedDashboardView()
        topology_data = view._get_enhanced_topology_data()
        
        print(f"   • Devices found: {len(topology_data.get('devices', []))}")
        print(f"   • Sites found: {len(topology_data.get('sites', []))}")
        print(f"   • Connections found: {len(topology_data.get('connections', []))}")
        
        if topology_data.get('error'):
            print(f"   ❌ Error: {topology_data['error']}")
        else:
            print(f"   ✅ Plugin data method working correctly!")
            
    except Exception as e:
        print(f"   ❌ Plugin test failed: {e}")
    
except ImportError as e:
    print(f"❌ Failed to import NetBox models: {e}")
    print("💡 Make sure you're running this script in the NetBox environment")
except Exception as e:
    print(f"❌ Analysis failed: {e}")
