import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser
from grocery.models import GroceryStore, GroceryCategory, GroceryProduct


print("=" * 60)
print("🛒 Creating Sample Grocery Data")
print("=" * 60)


def get_or_create_owner(username, email, password, first_name, last_name):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': 'grocery'
        }
    )
    if created:
        user.set_password(password)
        user.save()
    return user


# ========== Store 1: Fresh Mart ==========
owner1 = get_or_create_owner('fresh_mart', 'fresh@test.com', 'test123', 'Ramesh', 'Patel')

s1, created = GroceryStore.objects.get_or_create(
    owner=owner1,
    defaults={
        'name': 'Fresh Mart',
        'description': 'Fresh vegetables, fruits and daily essentials delivered in minutes.',
        'address': '12 Jayanagar, Bangalore',
        'phone': '9876543201',
        'rating': 4.7,
        'total_reviews': 428,
        'delivery_time': 15,
        'delivery_fee': 25,
        'min_order': 100,
    }
)

if created:
    veg = GroceryCategory.objects.create(store=s1, name='Vegetables', display_order=1)
    fruits = GroceryCategory.objects.create(store=s1, name='Fruits', display_order=2)
    dairy = GroceryCategory.objects.create(store=s1, name='Dairy & Eggs', display_order=3)
    staples = GroceryCategory.objects.create(store=s1, name='Staples', display_order=4)
    
    # Vegetables
    GroceryProduct.objects.create(store=s1, category=veg, name='Tomato', price=40, unit='kg', stock=100)
    GroceryProduct.objects.create(store=s1, category=veg, name='Onion', price=35, unit='kg', stock=150)
    GroceryProduct.objects.create(store=s1, category=veg, name='Potato', price=30, unit='kg', stock=200)
    GroceryProduct.objects.create(store=s1, category=veg, name='Carrot', price=55, unit='kg', stock=80)
    GroceryProduct.objects.create(store=s1, category=veg, name='Spinach', price=25, unit='pack', stock=60)
    GroceryProduct.objects.create(store=s1, category=veg, name='Cauliflower', price=45, unit='pcs', stock=40)
    
    # Fruits
    GroceryProduct.objects.create(store=s1, category=fruits, name='Banana', price=50, unit='dozen', stock=90)
    GroceryProduct.objects.create(store=s1, category=fruits, name='Apple', price=180, unit='kg', stock=50)
    GroceryProduct.objects.create(store=s1, category=fruits, name='Orange', price=120, unit='kg', stock=70)
    GroceryProduct.objects.create(store=s1, category=fruits, name='Grapes', price=90, unit='kg', stock=45)
    GroceryProduct.objects.create(store=s1, category=fruits, name='Mango', price=250, unit='kg', stock=30)
    
    # Dairy
    GroceryProduct.objects.create(store=s1, category=dairy, name='Milk', price=60, unit='ltr', stock=100)
    GroceryProduct.objects.create(store=s1, category=dairy, name='Curd', price=45, unit='pack', stock=80)
    GroceryProduct.objects.create(store=s1, category=dairy, name='Paneer', price=350, unit='kg', stock=25)
    GroceryProduct.objects.create(store=s1, category=dairy, name='Eggs', price=75, unit='dozen', stock=120, is_vegetarian=False)
    GroceryProduct.objects.create(store=s1, category=dairy, name='Butter', price=120, unit='pack', stock=40)
    
    # Staples
    GroceryProduct.objects.create(store=s1, category=staples, name='Rice (Basmati)', price=120, unit='kg', stock=200)
    GroceryProduct.objects.create(store=s1, category=staples, name='Wheat Flour', price=55, unit='kg', stock=150)
    GroceryProduct.objects.create(store=s1, category=staples, name='Toor Dal', price=140, unit='kg', stock=90)
    GroceryProduct.objects.create(store=s1, category=staples, name='Cooking Oil', price=180, unit='ltr', stock=60)
    
    print("✅ Created: Fresh Mart with 20 products")
else:
    print("ℹ️  Fresh Mart already exists")


# ========== Store 2: Daily Needs ==========
owner2 = get_or_create_owner('daily_needs', 'daily@test.com', 'test123', 'Suresh', 'Kumar')

s2, created = GroceryStore.objects.get_or_create(
    owner=owner2,
    defaults={
        'name': 'Daily Needs Kirana',
        'description': 'Your neighborhood kirana store - everything you need daily.',
        'address': '45 Koramangala, Bangalore',
        'phone': '9876543202',
        'rating': 4.5,
        'total_reviews': 312,
        'delivery_time': 20,
        'delivery_fee': 20,
        'min_order': 80,
    }
)

if created:
    snacks = GroceryCategory.objects.create(store=s2, name='Snacks & Biscuits', display_order=1)
    bev = GroceryCategory.objects.create(store=s2, name='Beverages', display_order=2)
    personal = GroceryCategory.objects.create(store=s2, name='Personal Care', display_order=3)
    household = GroceryCategory.objects.create(store=s2, name='Household', display_order=4)
    
    # Snacks
    GroceryProduct.objects.create(store=s2, category=snacks, name='Lays Chips', price=20, unit='pack', stock=200)
    GroceryProduct.objects.create(store=s2, category=snacks, name='Kurkure', price=20, unit='pack', stock=180)
    GroceryProduct.objects.create(store=s2, category=snacks, name='Marie Biscuits', price=30, unit='pack', stock=150)
    GroceryProduct.objects.create(store=s2, category=snacks, name='Parle-G', price=10, unit='pack', stock=300)
    GroceryProduct.objects.create(store=s2, category=snacks, name='Oreo Cookies', price=40, unit='pack', stock=100)
    
    # Beverages
    GroceryProduct.objects.create(store=s2, category=bev, name='Coca Cola', price=40, unit='ltr', stock=120)
    GroceryProduct.objects.create(store=s2, category=bev, name='Pepsi', price=40, unit='ltr', stock=100)
    GroceryProduct.objects.create(store=s2, category=bev, name='Frooti', price=20, unit='pack', stock=150)
    GroceryProduct.objects.create(store=s2, category=bev, name='Tea Powder', price=280, unit='pack', stock=60)
    GroceryProduct.objects.create(store=s2, category=bev, name='Coffee', price=420, unit='pack', stock=40)
    
    # Personal Care
    GroceryProduct.objects.create(store=s2, category=personal, name='Colgate Toothpaste', price=95, unit='pack', stock=80)
    GroceryProduct.objects.create(store=s2, category=personal, name='Dove Soap', price=65, unit='pcs', stock=100)
    GroceryProduct.objects.create(store=s2, category=personal, name='Head & Shoulders', price=240, unit='pack', stock=50)
    GroceryProduct.objects.create(store=s2, category=personal, name='Gillette Razor', price=180, unit='pack', stock=30)
    
    # Household
    GroceryProduct.objects.create(store=s2, category=household, name='Surf Excel', price=220, unit='pack', stock=90)
    GroceryProduct.objects.create(store=s2, category=household, name='Vim Dishwash', price=95, unit='pack', stock=110)
    GroceryProduct.objects.create(store=s2, category=household, name='Harpic Cleaner', price=180, unit='ltr', stock=60)
    GroceryProduct.objects.create(store=s2, category=household, name='Phenyl', price=85, unit='ltr', stock=70)
    
    print("✅ Created: Daily Needs Kirana with 18 products")
else:
    print("ℹ️  Daily Needs Kirana already exists")


# ========== Store 3: Organic Basket ==========
owner3 = get_or_create_owner('organic_basket', 'organic@test.com', 'test123', 'Meena', 'Reddy')

s3, created = GroceryStore.objects.get_or_create(
    owner=owner3,
    defaults={
        'name': 'Organic Basket',
        'description': '100% organic vegetables, fruits and products - chemical free.',
        'address': '78 Indiranagar, Bangalore',
        'phone': '9876543203',
        'rating': 4.8,
        'total_reviews': 189,
        'delivery_time': 30,
        'delivery_fee': 40,
        'min_order': 200,
    }
)

if created:
    organic_veg = GroceryCategory.objects.create(store=s3, name='Organic Vegetables', display_order=1)
    organic_fruits = GroceryCategory.objects.create(store=s3, name='Organic Fruits', display_order=2)
    organic_grains = GroceryCategory.objects.create(store=s3, name='Organic Grains', display_order=3)
    
    # Organic Veg
    GroceryProduct.objects.create(store=s3, category=organic_veg, name='Organic Tomato', price=80, unit='kg', stock=50, description='Farm fresh organic tomatoes')
    GroceryProduct.objects.create(store=s3, category=organic_veg, name='Organic Spinach', price=60, unit='pack', stock=40, description='Fresh organic spinach leaves')
    GroceryProduct.objects.create(store=s3, category=organic_veg, name='Organic Carrots', price=90, unit='kg', stock=35)
    GroceryProduct.objects.create(store=s3, category=organic_veg, name='Organic Broccoli', price=140, unit='kg', stock=25)
    
    # Organic Fruits
    GroceryProduct.objects.create(store=s3, category=organic_fruits, name='Organic Apple', price=280, unit='kg', stock=30)
    GroceryProduct.objects.create(store=s3, category=organic_fruits, name='Organic Banana', price=80, unit='dozen', stock=45)
    GroceryProduct.objects.create(store=s3, category=organic_fruits, name='Organic Strawberry', price=320, unit='pack', stock=15)
    
    # Organic Grains
    GroceryProduct.objects.create(store=s3, category=organic_grains, name='Organic Brown Rice', price=180, unit='kg', stock=60)
    GroceryProduct.objects.create(store=s3, category=organic_grains, name='Organic Quinoa', price=380, unit='kg', stock=20)
    GroceryProduct.objects.create(store=s3, category=organic_grains, name='Organic Oats', price=220, unit='kg', stock=40)
    
    print("✅ Created: Organic Basket with 10 products")
else:
    print("ℹ️  Organic Basket already exists")


print("\n" + "=" * 60)
print("✅ SAMPLE GROCERY DATA READY!")
print("=" * 60)
print(f"\n📊 SUMMARY:")
print(f"   Grocery Stores: {GroceryStore.objects.count()}")
print(f"   Categories: {GroceryCategory.objects.count()}")
print(f"   Products: {GroceryProduct.objects.count()}")
print(f"\n🔑 GROCERY OWNER LOGINS:")
print(f"   fresh_mart / test123")
print(f"   daily_needs / test123")
print(f"   organic_basket / test123")
print("=" * 60)