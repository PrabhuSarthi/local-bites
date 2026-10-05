\# LocalBites



A multi-service hyperlocal delivery platform built with Django.



\*\*One platform for local food shops, grocery stores, and ride bookings.\*\*



\---



\## Overview



LocalBites is a Django web application that connects customers with local

restaurants, grocery stores, and ride captains in a single platform. The

goal is to help small, unregistered local businesses compete with big

national players like Swiggy, Zomato, and Uber by giving them a shared

digital storefront.



\---



\## Tech Stack



| Layer | Technology |

|---|---|

| Backend | Django 5.x (Python 3.14) |

| Database | SQLite (development) |

| Frontend | Django Templates + vanilla HTML/CSS/JS |

| Fonts | Inter (Google Fonts) |

| Icons | Font Awesome 6.5.1 |

| Auth | Django's built-in auth with custom user model |

| Media | Django FileField + ImageField (local storage) |



\---



\## Project Structure

localbites/

├── core/ # Project settings and root URL config

│ ├── settings.py

│ ├── urls.py

│ ├── asgi.py

│ └── wsgi.py

├── accounts/ # Users, auth, dashboards, admin panel

│ ├── models.py # CustomUser

│ ├── views.py # Auth + dashboards + admin + partner

│ ├── urls.py

│ └── forms.py

├── food/ # Restaurant ordering

│ ├── models.py # Restaurant, MenuCategory, FoodItem, Order, OrderItem

│ ├── views.py

│ └── urls.py

├── grocery/ # Grocery ordering

│ ├── models.py # GroceryStore, GroceryCategory, GroceryProduct,

│ │ # GroceryOrder, GroceryOrderItem

│ ├── views.py

│ └── urls.py

├── rides/ # Ride booking

│ ├── models.py # Captain, Ride, RideReview

│ ├── views.py

│ └── urls.py

├── notifications/ # Cross-app notifications

│ ├── models.py # Notification

│ ├── views.py

│ └── urls.py

├── templates/ # All HTML templates

│ ├── base.html

│ ├── index.html

│ ├── accounts/

│ ├── admin\_panel/

│ ├── food/

│ ├── grocery/

│ ├── notifications/

│ ├── partner/

│ └── rides/

├── manage.py

└── db.sqlite3



text



\---



\## User Roles



The `CustomUser` model extends Django's `AbstractUser` with a `role` field.



| Role | Purpose |

|---|---|

| `admin` | Platform administrator |

| `customer` | End user (food, grocery, rides) |

| `restaurant` | Restaurant partner |

| `grocery` | Grocery store partner |

| `driver` | Ride captain |



Helper methods: `is\_admin()`, `is\_customer()`, `is\_restaurant()`,

`is\_grocery()`, `is\_driver()`.



\---



\## Data Models



\### accounts



\*\*CustomUser\*\* (`users` table)

\- `role` — admin / customer / restaurant / grocery / driver

\- `phone`, `address`, `profile\_pic`

\- `created\_at`, `updated\_at`

\- Inherits all Django user fields (username, email, password, etc.)



\### food



\*\*Restaurant\*\*

\- `owner` (OneToOne → CustomUser)

\- `name`, `description`, `image`, `address`, `phone`, `cuisine`

\- `opening\_time`, `closing\_time`

\- `rating`, `total\_reviews`, `delivery\_time`, `delivery\_fee`, `min\_order`

\- `is\_active`, `is\_approved`, `is\_open`

\- Helper: `is\_currently\_open()`, `get\_open\_status\_text()`



\*\*MenuCategory\*\*

\- `restaurant` (FK), `name`, `display\_order`



\*\*FoodItem\*\*

\- `restaurant` (FK), `category` (FK)

\- `name`, `description`, `image`, `price`

\- `is\_vegetarian`, `is\_available`, `preparation\_time`

\- `rating`, `times\_ordered`



\*\*Order\*\*

\- `order\_number` (auto: `ORD######`)

\- `customer` (FK), `restaurant` (FK)

\- `delivery\_address`, `phone`, `special\_instructions`

\- `subtotal`, `delivery\_fee`, `tax`, `total`

\- `status` — pending / confirmed / preparing / out\_for\_delivery / delivered / cancelled

\- `payment\_method`

\- `created\_at`, `confirmed\_at`, `delivered\_at`



\*\*OrderItem\*\*

\- `order` (FK), `food\_item` (FK), `quantity`, `price`



\### grocery



\*\*GroceryStore\*\*

\- `owner` (OneToOne → CustomUser)

\- `name`, `description`, `image`, `address`, `phone`

\- `rating`, `total\_reviews`, `delivery\_time`, `delivery\_fee`, `min\_order`

\- `is\_active`, `is\_approved`



\*\*GroceryCategory\*\*

\- `store` (FK), `name`, `display\_order`



\*\*GroceryProduct\*\*

\- `store` (FK), `category` (FK)

\- `name`, `description`, `image`, `price`, `unit`

\- `unit` — kg / g / ltr / ml / pcs / pack / dozen

\- `is\_vegetarian`, `is\_available`, `stock`

\- `times\_ordered`



\*\*GroceryOrder\*\*

\- `order\_number` (auto: `GRC######`)

\- `customer` (FK), `store` (FK)

\- `delivery\_address`, `phone`, `delivery\_slot`, `special\_instructions`

\- `subtotal`, `delivery\_fee`, `tax`, `total`

\- `status` — pending / confirmed / packing / out\_for\_delivery / delivered / cancelled



\*\*GroceryOrderItem\*\*

\- `order` (FK), `product` (FK), `quantity`, `price`



\### rides



\*\*Captain\*\*

\- `user` (OneToOne → CustomUser)

\- `vehicle\_type` — bike / auto / car

\- `vehicle\_number`, `vehicle\_model`, `license\_number`

\- `is\_online`, `is\_approved`

\- `rating`, `total\_rides`, `total\_earnings`

\- `current\_lat`, `current\_lng`



\*\*Ride\*\*

\- `ride\_number` (auto: `RID######`)

\- `customer` (FK), `captain` (FK, nullable)

\- `pickup\_address`, `drop\_address`, `distance\_km`

\- `vehicle\_type` — bike / auto / car

\- `estimated\_fare`, `final\_fare`

\- `status` — searching / accepted / arriving / started / completed / cancelled

\- `payment\_method`

\- `created\_at`, `accepted\_at`, `started\_at`, `completed\_at`



\*\*RideReview\*\*

\- `ride` (OneToOne), `customer` (FK), `rating`, `comment`



\### notifications



\*\*Notification\*\*

\- `user` (FK), `title`, `message`, `notification\_type`

\- `link`, `icon`, `is\_read`



\---



\## URL Map



\### Root (`core/urls.py`)



| URL | Maps To |

|---|---|

| `/admin/` | Django admin |

| `/` | Home (index.html) |

| `/` | accounts.urls |

| `/food/` | food.urls |

| `/grocery/` | grocery.urls |

| `/rides/` | rides.urls |

| `/notifications/` | notifications.urls |



\### accounts (`accounts/urls.py`)



| URL | View | Purpose |

|---|---|---|

| `/` | home\_view | Landing page |

| `/login/` | login\_view | Customer login |

| `/register/` | register\_view | Customer registration |

| `/logout/` | logout\_view | Logout |

| `/dashboard/` | dashboard\_view | Role-based dashboard |

| `/profile/` | profile\_view | User profile |

| `/profile/edit/` | edit\_profile\_view | Edit profile |

| `/admin-panel/` | admin\_dashboard | Admin dashboard |

| `/admin-panel/users/` | admin\_users | Manage users |

| `/admin-panel/orders/` | admin\_orders | All orders |

| `/admin-panel/rides/` | admin\_rides | All rides |

| `/admin-panel/partners/` | admin\_partners | Manage partners |

| `/partner/` | partner\_landing\_view | Partner landing |

| `/partner/login/` | partner\_login\_view | Partner login |

| `/partner/register/` | partner\_register\_view | Partner registration |

| `/partner/toggle-open/` | toggle\_restaurant\_open | Open/Close toggle |

| `/partner/earnings/` | partner\_earnings | Revenue dashboard |

| `/partner/reviews/` | partner\_reviews | Ratings + top items |

| `/partner/analytics/` | partner\_analytics | Sales analytics |

| `/partner/settings/` | partner\_settings | Restaurant settings |



\### food (`food/urls.py`)



| URL | View |

|---|---|

| `/food/` | restaurant\_list |

| `/food/restaurant/<id>/` | restaurant\_detail |

| `/food/api/cart/add/<id>/` | api\_add\_to\_cart (AJAX) |

| `/food/api/cart/decrease/<id>/` | api\_decrease\_cart (AJAX) |

| `/food/api/cart/remove/<id>/` | api\_remove\_from\_cart (AJAX) |

| `/food/menu/` | menu\_management |

| `/food/menu/add/` | add\_menu\_item |

| `/food/menu/category/add/` | add\_menu\_category |

| `/food/menu/<id>/edit/` | edit\_menu\_item |

| `/food/menu/<id>/delete/` | delete\_menu\_item |

| `/food/menu/<id>/toggle/` | api\_toggle\_item\_availability (AJAX) |

| `/food/cart/` | cart\_view |

| `/food/checkout/` | checkout\_view |

| `/food/orders/` | my\_orders |

| `/food/orders/<id>/` | order\_detail |

| `/food/restaurant-orders/` | restaurant\_orders |

| `/food/orders/<id>/status/` | update\_order\_status |



\### grocery, rides, notifications



Similar structure — list, detail, cart/booking, checkout, order/ride history,

partner order management.



\---



\## Key Features



\### Customer

\- Browse restaurants / grocery stores

\- Search + filter by cuisine

\- AJAX cart (add, increase, decrease, remove — no page reloads)

\- Checkout with delivery address + payment method

\- Order history + live status tracking

\- Notifications

\- Ride booking with captain assignment

\- Profile with order/ride stats



\### Restaurant Partner

\- Role-based dashboard with revenue + order stats

\- Open/Close toggle

\- Full menu management (categories + items)

\- Add / Edit / Delete menu items

\- Veg / Non-Veg classification

\- AJAX availability toggle (In Stock / Out of Stock)

\- Order management with status updates

\- Earnings page — daily/weekly/monthly revenue from delivered orders

\- Reviews page — restaurant rating + top-rated + most-ordered items

\- Analytics page — revenue bar chart, order status breakdown, top 5 items

\- Settings page — edit restaurant details



\### Grocery Partner

\- Dashboard with stock alerts + revenue

\- Product management

\- Order management



\### Ride Captain

\- Online/Offline toggle

\- Ride requests

\- Earnings tracking

\- Ratings



\### Admin

\- Platform-wide dashboard

\- User management with role filter + search

\- All orders (food + grocery)

\- All rides + captains

\- Partner management



\---



\## Running Locally



\### Prerequisites

\- Python 3.10+

\- pip

\- A terminal



\### Setup



```bash

\# 1. Navigate to the project

cd localbites



\# 2. Create and activate a virtual environment

python -m venv venv

venv\\Scripts\\activate         # Windows

source venv/bin/activate      # Mac/Linux



\# 3. Install dependencies

pip install django pillow



\# 4. Run migrations

python manage.py migrate



\# 5. Create a superuser (optional, for /admin/)

python manage.py createsuperuser



\# 6. Load demo data (optional)

python create\_food\_data.py

python create\_grocery\_data.py

python create\_rides\_data.py



\# 7. Start the server

python manage.py runserver

Then visit http://127.0.0.1:8000/



Design Language

LocalBites uses a consistent dark glassmorphism UI:



Element	Value

Font	Inter (400–900)

Base background	#08080C

Card background	linear-gradient(160deg, rgba(28,28,42,0.6), rgba(18,18,28,0.8))

Card border	rgba(255,255,255,0.08)

Primary gradient	linear-gradient(135deg, #6366F1, #8B5CF6)

Accent gradient	linear-gradient(135deg, #818CF8, #22D3EE)

Success	#22C55E

Danger	#EF4444

Warning	#F59E0B

Border radius	12–24px (cards), 100px (pills)

Signature effects	Radial gradient glows + subtle grid overlay

Icons: Font Awesome 6.5.1



Current Status

Working today:



Full authentication (customer, partner, admin)



Restaurant browsing, ordering, and management



Grocery store browsing, ordering, and management



Ride booking



Notifications system



Admin panel



4 partner business pages (Earnings, Reviews, Analytics, Settings)



Planned / roadmap:



Platform-owned delivery fee (currently set per-restaurant)



Commission model (10–15% per order for platform revenue)



Real-time rider tracking



Payment gateway integration (Razorpay / Stripe)



Distance-based dynamic delivery fees



Promo codes + loyalty



Mobile app (React Native)



Business Model (Planned)

LocalBites will generate revenue through:



Commission — 10–15% of subtotal per order



Delivery fee — owned by the platform, split with riders



Platform fee — small fixed fee per order



Promoted listings — optional paid visibility for partners



Example on a ₹500 order:



Line	Amount	Goes To

Subtotal	₹500	—

Tax (5%)	₹25	Government

Delivery Fee	₹40	₹15 LocalBites + ₹25 Rider

Platform Fee	₹10	LocalBites

Customer Pays	₹575	—

Commission (12%)	₹60	LocalBites

Restaurant Earns	₹440	Restaurant

LocalBites Earns	₹85	LocalBites

License

This is a personal/portfolio project. All rights reserved.



Author

Built by prabhu  as a full-stack Django portfolio project.



For questions or collaboration: open an issue on the repo

