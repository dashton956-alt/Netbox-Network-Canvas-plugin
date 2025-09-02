#!/usr/bin/env python3
"""
Simple cable creation test for NetBox v4.3.7
"""

def create_test_cables():
    """Create test cables between devices"""
    print("🔌 Testing cable creation in NetBox...")
    
    try:
        # Import required models
        from dcim.models import Device, Interface, Cable
        from django.db import transaction
        
        # Check current cables
        existing_cables = Cable.objects.count()
        print(f"📊 Existing cables: {existing_cables}")
        
        # Get some devices to connect
        devices = Device.objects.select_related('site')[:5]
        print(f"📊 Available devices: {len(devices)}")
        
        for device in devices:
            print(f"   • {device.name} ({device.site.name if device.site else 'No Site'})")
            interfaces = device.interfaces.all()[:3]
            for interface in interfaces:
                print(f"     - Interface: {interface.name} (Type: {interface.type})")
        
        if len(devices) < 2:
            print("❌ Need at least 2 devices to create cables")
            return
        
        # Try to create a simple cable
        device_a = devices[0]
        device_b = devices[1]
        
        # Get interfaces
        interface_a = device_a.interfaces.first()
        interface_b = device_b.interfaces.first()
        
        if not interface_a or not interface_b:
            print("❌ Devices don't have interfaces")
            return
        
        print(f"🔗 Attempting to connect:")
        print(f"   Device A: {device_a.name} - Interface: {interface_a.name}")
        print(f"   Device B: {device_b.name} - Interface: {interface_b.name}")
        
        # Check NetBox version for cable creation method
        try:
            # Try NetBox v4+ method
            with transaction.atomic():
                cable = Cable.objects.create(
                    type='cat6',
                    status='connected',
                    length=5,
                    length_unit='m'
                )
                
                # Add terminations
                from dcim.models import CableTermination
                CableTermination.objects.create(
                    cable=cable,
                    termination=interface_a
                )
                CableTermination.objects.create(
                    cable=cable,
                    termination=interface_b
                )
                
                print(f"✅ Created cable {cable.id} using CableTermination model")
                
        except Exception as e1:
            print(f"⚠️ CableTermination method failed: {e1}")
            
            try:
                # Try legacy method
                cable = Cable(
                    termination_a=interface_a,
                    termination_b=interface_b,
                    type='cat6',
                    status='connected',
                    length=5,
                    length_unit='m'
                )
                cable.save()
                print(f"✅ Created cable {cable.id} using legacy method")
                
            except Exception as e2:
                print(f"❌ Legacy method also failed: {e2}")
                print("💡 Manual cable creation needed through NetBox UI")
                return
        
        # Check final cable count
        final_cables = Cable.objects.count()
        print(f"📊 Final cable count: {final_cables}")
        
        # List some cables with their terminations
        print("\n🔍 Existing cables:")
        for cable in Cable.objects.all()[:5]:
            print(f"   Cable {cable.id}: Status={cable.status}, Type={cable.type}")
            
            # Check terminations
            if hasattr(cable, 'a_terminations'):
                a_terms = list(cable.a_terminations.all())
                print(f"     A-side: {len(a_terms)} terminations")
                for term in a_terms[:2]:
                    if hasattr(term, 'termination') and hasattr(term.termination, 'device'):
                        print(f"       - {term.termination.device.name}:{term.termination.name}")
            
            if hasattr(cable, 'b_terminations'):
                b_terms = list(cable.b_terminations.all())
                print(f"     B-side: {len(b_terms)} terminations")
                for term in b_terms[:2]:
                    if hasattr(term, 'termination') and hasattr(term.termination, 'device'):
                        print(f"       - {term.termination.device.name}:{term.termination.name}")
                        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Setup Django
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
    django.setup()
    
    create_test_cables()
