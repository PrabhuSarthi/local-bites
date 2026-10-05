import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser
from food.models import Restaurant, MenuCategory, FoodItem


print("=" * 60)
print("🍽️ Creating Sample Restaurant & Food Data")
print("=" * 60)


# Get restaurant owners (or create them)
def get_or_create_owner(username, email, password, first_name, last_name):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': 'restaurant'
        }
    )
    if created:
        user.set_password(password)
        user.save()
    return user


# Restaurant 1: Spice Garden
owner1 = get_or_create_owner('spice_garden', 'spice@test.com', 'test123', 'Rajesh', 'Kumar')

r1, created = Restaurant.objects.get_or_create(
    owner=owner1,
    defaults={
        'name': 'Spice Garden',
        'description': 'Authentic North Indian cuisine with rich flavors and fresh ingredients.',
        'address': '123 MG Road, Bangalore',
        'phone': '9876543210',
        'cuisine': 'North Indian',
        'rating': 4.7,
        'total_reviews': 342,
        'delivery_time': 30,
        'delivery_fee': 40,
        'min_order': 150,
    }
)

if created:
    # Categories
    starters = MenuCategory.objects.create(restaurant=r1, name='Starters', display_order=1)
    mains = MenuCategory.objects.create(restaurant=r1, name='Main Course', display_order=2)
    breads = MenuCategory.objects.create(restaurant=r1, name='Breads', display_order=3)
    desserts = MenuCategory.objects.create(restaurant=r1, name='Desserts', display_order=4)
    
    # Food items
    FoodItem.objects.create(restaurant=r1, category=starters, name='Paneer Tikka', price=280, description='Grilled cottage cheese with spices', is_vegetarian=True, rating=4.8)
    FoodItem.objects.create(restaurant=r1, category=starters, name='Chicken Tikka', price=320, description='Tender chicken in yogurt marinade', is_vegetarian=False, rating=4.7)
    FoodItem.objects.create(restaurant=r1, category=starters, name='Veg Spring Rolls', price=180, description='Crispy rolls with veggies', is_vegetarian=True, rating=4.5)
    
    FoodItem.objects.create(restaurant=r1, category=mains, name='Butter Chicken', price=380, description='Creamy tomato curry with tender chicken', is_vegetarian=False, rating=4.9)
    FoodItem.objects.create(restaurant=r1, category=mains, name='Paneer Butter Masala', price=320, description='Cottage cheese in rich gravy', is_vegetarian=True, rating=4.8)
    FoodItem.objects.create(restaurant=r1, category=mains, name='Dal Makhani', price=260, description='Slow-cooked black lentils', is_vegetarian=True, rating=4.6)
    FoodItem.objects.create(restaurant=r1, category=mains, name='Chicken Biryani', price=350, description='Aromatic basmati rice with chicken', is_vegetarian=False, rating=4.9)
    
    FoodItem.objects.create(restaurant=r1, category=breads, name='Butter Naan', price=60, description='Soft flatbread with butter', is_vegetarian=True, rating=4.7)
    FoodItem.objects.create(restaurant=r1, category=breads, name='Garlic Naan', price=80, description='Naan with fresh garlic', is_vegetarian=True, rating=4.8)
    FoodItem.objects.create(restaurant=r1, category=breads, name='Tandoori Roti', price=40, description='Whole wheat flatbread', is_vegetarian=True, rating=4.5)
    
    FoodItem.objects.create(restaurant=r1, category=desserts, name='Gulab Jamun', price=120, description='Sweet dumplings in syrup', is_vegetarian=True, rating=4.8)
    FoodItem.objects.create(restaurant=r1, category=desserts, name='Rasmalai', price=150, description='Cottage cheese in saffron milk', is_vegetarian=True, rating=4.9)
    
    print("✅ Created: Spice Garden with 12 items")
else:
    print("ℹ️  Spice Garden already exists")


# Restaurant 2: Pizza Palace
owner2 = get_or_create_owner('pizza_palace', 'pizza@test.com', 'test123', 'Amit', 'Verma')

r2, created = Restaurant.objects.get_or_create(
    owner=owner2,
    defaults={
        'name': 'Pizza Palace',
        'description': 'Wood-fired pizzas with premium ingredients, delivered hot.',
        'address': '456 Church Street, Bangalore',
        'phone': '9876543211',
        'cuisine': 'Italian',
        'rating': 4.6,
        'total_reviews': 289,
        'delivery_time': 25,
        'delivery_fee': 50,
        'min_order': 200,
    }
)

if created:
    pizzas = MenuCategory.objects.create(restaurant=r2, name='Pizzas', display_order=1)
    sides = MenuCategory.objects.create(restaurant=r2, name='Sides', display_order=2)
    drinks = MenuCategory.objects.create(restaurant=r2, name='Beverages', display_order=3)
    
    FoodItem.objects.create(restaurant=r2, category=pizzas, name='Margherita Pizza', price=299, description='Classic cheese and tomato', is_vegetarian=True, rating=4.7)
    FoodItem.objects.create(restaurant=r2, category=pizzas, name='Pepperoni Pizza', price=449, description='Loaded with pepperoni', is_vegetarian=False, rating=4.8)
    FoodItem.objects.create(restaurant=r2, category=pizzas, name='Veggie Supreme', price=399, description='Bell peppers, olives, mushrooms', is_vegetarian=True, rating=4.6)
    FoodItem.objects.create(restaurant=r2, category=pizzas, name='BBQ Chicken Pizza', price=499, description='BBQ sauce with grilled chicken', is_vegetarian=False, rating=4.9)
    
    FoodItem.objects.create(restaurant=r2, category=sides, name='Garlic Bread', price=149, description='Crispy garlic butter bread', is_vegetarian=True, rating=4.5)
    FoodItem.objects.create(restaurant=r2, category=sides, name='Cheesy Nachos', price=199, description='Nachos with cheese sauce', is_vegetarian=True, rating=4.6)
    
    FoodItem.objects.create(restaurant=r2, category=drinks, name='Cold Coffee', price=120, description='Iced coffee with cream', is_vegetarian=True, rating=4.7)
    FoodItem.objects.create(restaurant=r2, category=drinks, name='Fresh Lime Soda', price=80, description='Refreshing lime drink', is_vegetarian=True, rating=4.4)
    
    print("✅ Created: Pizza Palace with 8 items")
else:
    print("ℹ️  Pizza Palace already exists")


# Restaurant 3: Biryani House
owner3 = get_or_create_owner('biryani_house', 'biryani@test.com', 'test123', 'Karthik', 'Reddy')

r3, created = Restaurant.objects.get_or_create(
    owner=owner3,
    defaults={
        'name': 'Biryani House',
        'description': 'Authentic Hyderabadi biryani cooked in traditional dum style.',
        'address': '789 Brigade Road, Bangalore',
        'phone': '9876543212',
        'cuisine': 'Hyderabadi',
        'rating': 4.8,
        'total_reviews': 512,
        'delivery_time': 35,
        'delivery_fee': 40,
        'min_order': 250,
    }
)

if created:
    biryanis = MenuCategory.objects.create(restaurant=r3, name='Biryanis', display_order=1)
    kebabs = MenuCategory.objects.create(restaurant=r3, name='Kebabs', display_order=2)
    
    FoodItem.objects.create(restaurant=r3, category=biryanis, name='Chicken Dum Biryani', price=320, description='Slow-cooked in sealed pot', is_vegetarian=False, rating=4.9)
    FoodItem.objects.create(restaurant=r3, category=biryanis, name='Mutton Biryani', price=420, description='Tender mutton with aromatic rice', is_vegetarian=False, rating=4.9)
    FoodItem.objects.create(restaurant=r3, category=biryanis, name='Veg Biryani', price=250, description='Mixed vegetables with basmati', is_vegetarian=True, rating=4.5)
    FoodItem.objects.create(restaurant=r3, category=biryanis, name='Egg Biryani', price=220, description='Boiled eggs in biryani masala', is_vegetarian=False, rating=4.6)
    
    FoodItem.objects.create(restaurant=r3, category=kebabs, name='Chicken Seekh Kebab', price=280, description='Minced chicken skewers', is_vegetarian=False, rating=4.7)
    FoodItem.objects.create(restaurant=r3, category=kebabs, name='Paneer Tikka Kebab', price=260, description='Grilled paneer cubes', is_vegetarian=True, rating=4.6)
    
    print("✅ Created: Biryani House with 6 items")
else:
    print("ℹ️  Biryani House already exists")


# Restaurant 4: South Indian Delights
owner4 = get_or_create_owner('south_delights', 'south@test.com', 'test123', 'Lakshmi', 'Iyengar')

r4, created = Restaurant.objects.get_or_create(
    owner=owner4,
    defaults={
        'name': 'South Indian Delights',
        'description': 'Traditional dosas, idlis, and more — crispy and authentic.',
        'address': '321 Jayanagar, Bangalore',
        'phone': '9876543213',
        'cuisine': 'South Indian',
        'rating': 4.7,
        'total_reviews': 428,
        'delivery_time': 20,
        'delivery_fee': 30,
        'min_order': 100,
    }
)

if created:
    dosa = MenuCategory.objects.create(restaurant=r4, name='Dosas', display_order=1)
    rice = MenuCategory.objects.create(restaurant=r4, name='Rice Items', display_order=2)
    bevs = MenuCategory.objects.create(restaurant=r4, name='Beverages', display_order=3)
    
    FoodItem.objects.create(restaurant=r4, category=dosa, name='Masala Dosa', price=120, description='Crispy dosa with potato filling', is_vegetarian=True, rating=4.8)
    FoodItem.objects.create(restaurant=r4, category=dosa, name='Plain Dosa', price=80, description='Classic crispy dosa', is_vegetarian=True, rating=4.6)
    FoodItem.objects.create(restaurant=r4, category=dosa, name='Ghee Roast Dosa', price=150, description='Extra crispy with ghee', is_vegetarian=True, rating=4.9)
    FoodItem.objects.create(restaurant=r4, category=dosa, name='Set Dosa', price=100, description='Soft fluffy dosas (3 pcs)', is_vegetarian=True, rating=4.5)
    
    FoodItem.objects.create(restaurant=r4, category=rice, name='Bisi Bele Bath', price=90, description='Spiced rice with lentils', is_vegetarian=True, rating=4.6)
    FoodItem.objects.create(restaurant=r4, category=rice, name='Curd Rice', price=70, description='Cooling yogurt rice', is_vegetarian=True, rating=4.4)
    FoodItem.objects.create(restaurant=r4, category=rice, name='Lemon Rice', price=80, description='Tangy turmeric rice', is_vegetarian=True, rating=4.5)
    
    FoodItem.objects.create(restaurant=r4, category=bevs, name='Filter Coffee', price=50, description='Authentic South Indian filter coffee', is_vegetarian=True, rating=4.9)
    FoodItem.objects.create(restaurant=r4, category=bevs, name='Masala Chai', price=40, description='Spiced tea', is_vegetarian=True, rating=4.7)
    
    print("✅ Created: South Indian Delights with 9 items")
else:
    print("ℹ️  South Indian Delights already exists")


# Restaurant 5: Chinese Wok
owner5 = get_or_create_owner('chinese_wok', 'chinese@test.com', 'test123', 'Wei', 'Chen')

r5, created = Restaurant.objects.get_or_create(
    owner=owner5,
    defaults={
        'name': 'Chinese Wok',
        'description': 'Indo-Chinese favorites with fresh ingredients and bold flavors.',
        'address': '654 Koramangala, Bangalore',
        'phone': '9876543214',
        'cuisine': 'Chinese',
        'rating': 4.5,
        'total_reviews': 267,
        'delivery_time': 30,
        'delivery_fee': 40,
        'min_order': 150,
    }
)

if created:
    noodles = MenuCategory.objects.create(restaurant=r5, name='Noodles', display_order=1)
    rice_cat = MenuCategory.objects.create(restaurant=r5, name='Rice', display_order=2)
    starters_c = MenuCategory.objects.create(restaurant=r5, name='Starters', display_order=3)
    
    FoodItem.objects.create(restaurant=r5, category=noodles, name='Hakka Noodles', price=180, description='Stir-fried noodles with veggies', is_vegetarian=True, rating=4.5)
    FoodItem.objects.create(restaurant=r5, category=noodles, name='Chicken Noodles', price=220, description='Noodles with chicken', is_vegetarian=False, rating=4.6)
    FoodItem.objects.create(restaurant=r5, category=noodles, name='Schezwan Noodles', price=200, description='Spicy Schezwan style', is_vegetarian=True, rating=4.7)
    
    FoodItem.objects.create(restaurant=r5, category=rice_cat, name='Fried Rice', price=180, description='Classic veg fried rice', is_vegetarian=True, rating=4.5)
    FoodItem.objects.create(restaurant=r5, category=rice_cat, name='Chicken Fried Rice', price=230, description='Wok-tossed chicken rice', is_vegetarian=False, rating=4.7)
    
    FoodItem.objects.create(restaurant=r5, category=starters_c, name='Veg Manchurian', price=190, description='Crispy veggie balls in sauce', is_vegetarian=True, rating=4.6)
    FoodItem.objects.create(restaurant=r5, category=starters_c, name='Chicken Manchurian', price=240, description='Chicken in Manchurian sauce', is_vegetarian=False, rating=4.7)
    FoodItem.objects.create(restaurant=r5, category=starters_c, name='Spring Rolls', price=150, description='Crispy veggie rolls', is_vegetarian=True, rating=4.4)
    
    print("✅ Created: Chinese Wok with 8 items")
else:
    print("ℹ️  Chinese Wok already exists")


print("\n" + "=" * 60)
print("✅ SAMPLE FOOD DATA READY!")
print("=" * 60)
print(f"\n📊 SUMMARY:")
print(f"   Restaurants: {Restaurant.objects.count()}")
print(f"   Menu Categories: {MenuCategory.objects.count()}")
print(f"   Food Items: {FoodItem.objects.count()}")
print(f"\n🔑 RESTAURANT OWNER LOGINS (for testing):")
print(f"   spice_garden / test123")
print(f"   pizza_palace / test123")
print(f"   biryani_house / test123")
print(f"   south_delights / test123")
print(f"   chinese_wok / test123")
print("=" * 60)