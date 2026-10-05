import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser
from rides.models import Captain


print("=" * 60)
print("🏍️ Creating Sample Captains Data")
print("=" * 60)


def create_captain(username, email, password, first_name, last_name, vehicle_type, vehicle_number, vehicle_model, rating=4.8):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': 'driver'
        }
    )
    if created:
        user.set_password(password)
        user.save()
    
    captain, captain_created = Captain.objects.get_or_create(
        user=user,
        defaults={
            'vehicle_type': vehicle_type,
            'vehicle_number': vehicle_number,
            'vehicle_model': vehicle_model,
            'rating': rating,
            'total_rides': 0,
            'is_online': True,
            'is_approved': True,
        }
    )
    
    if captain_created:
        print(f"✅ Created: {first_name} {last_name} ({vehicle_type} · {vehicle_number})")
    else:
        print(f"ℹ️  {first_name} {last_name} already exists")
    
    return captain


# Bike Captains
create_captain('captain_raju', 'raju@test.com', 'test123', 'Raju', 'Kumar', 'bike', 'KA-01-AB-1234', 'Honda Activa', 4.9)
create_captain('captain_suresh', 'suresh@test.com', 'test123', 'Suresh', 'Yadav', 'bike', 'KA-02-CD-5678', 'Bajaj Pulsar', 4.7)
create_captain('captain_amit', 'amit@test.com', 'test123', 'Amit', 'Singh', 'bike', 'KA-03-EF-9012', 'TVS Apache', 4.8)

# Auto Captains
create_captain('captain_mahesh', 'mahesh@test.com', 'test123', 'Mahesh', 'Patel', 'auto', 'KA-04-GH-3456', 'Bajaj RE', 4.6)
create_captain('captain_venkat', 'venkat@test.com', 'test123', 'Venkat', 'Rao', 'auto', 'KA-05-IJ-7890', 'Piaggio Ape', 4.7)

# Car Captains
create_captain('captain_rajesh', 'rajesh@test.com', 'test123', 'Rajesh', 'Sharma', 'car', 'KA-06-KL-2345', 'Maruti Swift', 4.9)
create_captain('captain_karthik', 'karthik@test.com', 'test123', 'Karthik', 'Reddy', 'car', 'KA-07-MN-6789', 'Hyundai i20', 4.8)


print("\n" + "=" * 60)
print("✅ SAMPLE CAPTAINS READY!")
print("=" * 60)
print(f"\n📊 SUMMARY:")
print(f"   Total Captains: {Captain.objects.count()}")
print(f"   Bikes: {Captain.objects.filter(vehicle_type='bike').count()}")
print(f"   Autos: {Captain.objects.filter(vehicle_type='auto').count()}")
print(f"   Cars: {Captain.objects.filter(vehicle_type='car').count()}")
print(f"\n🔑 CAPTAIN LOGINS (for testing):")
print(f"   captain_raju / test123 (Bike)")
print(f"   captain_mahesh / test123 (Auto)")
print(f"   captain_rajesh / test123 (Car)")
print("=" * 60)