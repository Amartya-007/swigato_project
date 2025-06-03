# Swigato 🍔🍕🍟 – The Food App I Wish My Hostel Had

## *A Python Project by Amartya Vishwakarma (a.k.a. That Guy Who Codes at 2AM)*

Hey there, fellow coder, foodie, or random internet traveler! I’m **Amartya Vishwakarma**, and this is **Swigato** – my not-so-humble attempt to bring Swiggy/Zomato vibes to my laptop (minus the actual food delivery, sorry, you still gotta walk to the mess).

This project started as a CLI app for a college assignment, but then I got carried away. Now it’s a full-blown GUI food ordering platform with admin superpowers, a database, and more features than my college canteen menu. Grab a snack and read on!

---

## 🚀 What Can You Do With Swigato?

### 👀 If You’re Just Browsing (Guest Mode)

- Browse all the restaurants (even the ones with suspicious hygiene).
- Check out detailed menus with prices and descriptions.
- Add food to your cart and place orders as a guest (no commitment, no judgment).
- Leave reviews and ratings (because everyone’s a critic).

### 🧑‍💻 If You’re a Registered User

- Sign up with a super-secure (bcrypt-hashed!) password.
- Log in and keep your foodie history forever (or until you uninstall).
- Everything a guest can do, plus:
  - See your order history (so you can regret your choices later).
  - Leave reviews that actually update the restaurant’s average rating.

### 🦸‍♂️ If You’re The Admin (a.k.a. Me)

- Access the secret Admin Dashboard (no cape required).
- Manage users: view, add, edit, or delete anyone (except yourself, for safety!).
- Manage restaurants: add new places, edit details, or nuke them (deletes their menu & reviews too – use wisely).
- Menu management: add, edit, or remove dishes for any restaurant.
- Order management: see all orders (user & guest), update statuses (Pending → Out for Delivery → Delivered), and judge people’s food choices.
- Review moderation: read and delete reviews if they’re spammy, mean, or just plain weird.

---

## 🛠️ Tech Stack (a.k.a. How I Made This Monster)

- **Python 3.x** – The brains of the operation.
- **CustomTkinter** – For that modern, not-ugly GUI.
- **SQLite** – File-based database, because I’m not paying for AWS.
- **bcrypt** – For password hashing, so even I can’t see your secrets.
- **Rich** – For making the CLI version look less like Notepad.
- **CTkTable** – For pretty tables in the GUI.
- **Pillow** – For images, because food apps need food pics.

---

## 🏗️ How It’s All Organized (a.k.a. My Digital Mess)

```text
├── admin
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (133.0 B)
│   │   └── actions.cpython-312.pyc (24.1 KB)
│   ├── __init__.py
│   └── actions.py (20.6 KB)
├── assets
│   ├── menu_items
│   │   ├── menu_1.jpeg (12.9 KB)
│   │   ├── menu_2.jpeg (12.1 KB)
│   │   ├── menu_3.jpeg (14.9 KB)
│   │   ├── menu_4.jpeg (13.8 KB)
│   │   ├── menu_5.jpeg (12.0 KB)
│   │   └── menu_default.jpg (44.2 KB)
│   └── restaurants
│       ├── badkul.jpeg (9.6 KB)
│       ├── default_restaurant.jpg (78.0 KB)
│       ├── resort-4471852_1280.jpg (250.6 KB)
│       ├── restaurant_test.jpg (8.3 MB)
│       ├── restaurent_a.jpeg (20.2 KB)
│       ├── restaurent_b.jpeg (10.3 KB)
│       ├── restaurent_c.jpeg (9.8 KB)
│       └── The_Great_Hall_Baluchi.jpg (279.4 KB)
├── cart
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (132.0 B)
│   │   └── models.cpython-312.pyc (6.8 KB)
│   ├── __init__.py
│   └── models.py (4.3 KB)
├── data
│   ├── remember_me.json (23.0 B)
│   ├── swigato_app.log (587.6 KB)
│   └── swigato.db (68.0 KB)
├── delivery
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (136.0 B)
│   │   └── tracker.cpython-312.pyc (857.0 B)
│   ├── __init__.py
│   └── tracker.py (573.0 B)
├── gui_components
│   ├── admin_dashboard.py (8.0 KB)
│   ├── admin_menus_screen.py (838.0 B)
│   ├── admin_orders_screen.py (8.7 KB)
│   ├── admin_restaurants_screen_new.py (9.8 KB)
│   ├── admin_restaurants_screen.py (9.8 KB)
│   ├── admin_reviews_screen.py (4.7 KB)
│   ├── admin_screen.py (27.3 KB)
│   ├── admin_users_screen_backup.py (39.1 KB)
│   ├── admin_users_screen.py (39.1 KB)
│   ├── cart_screen.py (7.9 KB)
│   ├── login_screen.py (9.6 KB)
│   ├── main_app_screen.py (12.7 KB)
│   ├── menu_screen.py (22.2 KB)
│   ├── restaurant_management_screen.py (52.6 KB)
│   ├── review_submission_screen.py (6.8 KB)
│   ├── signup_screen.py (10.5 KB)
│   └── swigato_dialog.py (3.5 KB)
├── orders
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (134.0 B)
│   │   └── models.cpython-312.pyc (11.9 KB)
│   ├── __init__.py
│   └── models.py (9.4 KB)
├── restaurants
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (139.0 B)
│   │   └── models.cpython-312.pyc (30.1 KB)
│   ├── __init__.py
│   └── models.py (23.4 KB)
├── reviews
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (135.0 B)
│   │   └── models.cpython-312.pyc (11.8 KB)
│   ├── __init__.py
│   └── models.py (10.7 KB)
├── users
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (133.0 B)
│   │   ├── auth.cpython-312.pyc (2.1 KB)
│   │   └── models.cpython-312.pyc (11.6 KB)
│   ├── __init__.py
│   ├── auth.py (1.6 KB)
│   └── models.py (8.4 KB)
├── utils
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc (133.0 B)
│   │   ├── database.cpython-312.pyc (9.8 KB)
│   │   ├── logger.cpython-312.pyc (2.1 KB)
│   │   └── validation.cpython-312.pyc (6.9 KB)
│   ├── __init__.py
│   ├── database.py (7.5 KB)
│   ├── image_loader.py (1.4 KB)
│   ├── logger.py (1.4 KB)
│   ├── update_schema.py (2.3 KB)
│   └── validation.py (7.8 KB)
├── .gitignore (1.2 KB)
├── gui_app.py (15.4 KB)
├── gui_constants.py (3.8 KB)
├── main.py (22.4 KB)
├── README.md (6.5 KB)
├── requirements.txt (42.0 B)
├── swigato_icon.ico (22.2 KB)
└── swigato_icon.png (1.2 MB)

```

---

## 🖥️ Main Features

- **Modern GUI**: CustomTkinter-powered, looks good even at 3AM.
- **Authentication**: Sign up, log in, bcrypt-hashed passwords (no plain text, promise).
- **Restaurant Discovery**: Browse, search, and drool over menus.
- **Cart System**: Add, remove, and update items before you commit to your cravings.
- **Order Placement**: Place orders as guest or user, with real-time status updates.
- **Order History**: Users can see all their past (questionable) food decisions.
- **Review System**: Leave reviews, rate restaurants, and see average ratings update live.
- **Admin Panel**: Manage users, restaurants, menus, orders, and reviews from a slick dashboard.
- **Review Moderation**: Admin can delete reviews that are too spicy (or just spam).
- **Database Integration**: All data is persistent – your midnight orders are safe forever.
- **Security**: bcrypt for passwords, input validation everywhere, and no SQL injection allowed.
- **Logging**: Everything gets logged, so I can debug your weird bugs.

---

## 🧑‍🔬 How To Run (a.k.a. Become a Swigato Power User)

1. **Clone the repo:**

   ```bash
   git clone https://github.com/Amartya-007/swigato_project
   cd swigato_project
   ```

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the GUI app:**

   ```bash
   python gui_app.py
   ```

   Or, for nostalgia, run the CLI version:

   ```bash
   
   python main.py
   ```

4. **First run?**
   - The app creates the database, tables, and a default admin user for you.
   - Sample restaurants and menu items are added so you’re not staring at an empty screen.

**Default Admin Login:**

- Username: `admin`
- Password: `admin123`

(Please change these if you’re not me. Seriously.)

---

## 🏆 Project Highlights & Fun Facts

- Started as a one-night assignment, became a semester-long obsession.
- Learned more about CTkinter, databases, and debugging than any textbook could teach.
- The admin can’t delete themselves (learned that the hard way).
- Every feature was tested by ordering imaginary biryani at 1AM.
- The codebase is modular, so adding new features is (almost) painless.

---

## 🔮 What’s Next? (a.k.a. My Wish List)

- Real-time order tracking (with fake delivery boys?)
- Payment gateway integration (Monopoly money, maybe?)
- Restaurant owner dashboard
- Mobile app (if I ever learn Kivy or Flutter)
- More analytics for admins (because graphs are cool)

---

## 👨‍💻 How it completed

This project is the result of too much caffeine, too little sleep, and a lot of Stack Overflow and of course **AI (My Partner in crime)**. If you read this far, you deserve a samosa. Or at least a star on GitHub. 😉

*“Why settle for basic when you can go big?”* – That’s how Swigato happened.

---

© 2025 Amartya Vishwakarma | Built with ❤️, Python, and way too much ☕
