# Swigato CLI - My Awesome Food App! 🍔🍕🍦

Hey there! This is **Amartya Vishwakarma**, and welcome to Swigato! This is a cool little command-line food ordering app I built. Think of it like a mini Swiggy or Zomato, but all in your terminal. I originally just stored data in memory, but then I was like, "Nah, let's make this legit," so I switched it over to use an SQLite database. That means all your user stuff, orders, and even those spicy reviews get saved properly.

I also used the `rich` library for Python to make the terminal output look way better – because who likes boring text, right? Plus, there's a whole admin section where you (or, well, *I*) can manage everything.

## So, What Can You Do Here?

### If You're Just Browsing (Guest Mode 😎)

* **Check out Restaurants:** See all the places you can order from.
* **Peep the Menu:** Look at what's cooking at any restaurant.
* **Toss Stuff in Your Cart:** Add items you're craving.
* **Order Up! (Guest Checkout):** Place your order without making an account. Your cart gets emptied after, nice and clean.

### If You're a Regular (Logged-In User 🤓)

* **Sign Up:** Easy peasy account creation. Your password? Super safe with `bcrypt` hashing.
* **Log In:** Get back to your foodie adventures.
* **Everything a Guest Can Do:** Obviously.
* **"Where's My Food?" (Order History):** Check up on your past orders.
* **Speak Your Mind (Add Reviews):** Loved it? Hated it? Let the world (and the restaurant) know. Your review even updates the restaurant's average rating – pretty neat, huh?

### If You're Me (Admin Superpowers! 🦸‍♂️)

* **Secret Admin Panel:** My control center for all things Swigato.
* **User Control:**
  * See everyone who's signed up.
  * Boot users if they're being naughty (but I can't delete myself, lol).
* **Order Overlord:**
  * View every single order, whether from a user or a guest.
  * Change order statuses – "Pending," "Out for Delivery," "Eaten," you name it.
* **Restaurant Boss:**
  * See all the restaurants in the system.
  * Add new foodie hotspots – name, what kind of food, where it is.
  * Fix any mistakes in restaurant details.
  * Nuke a restaurant if it closes down (this also gets rid of its menu and reviews, so, like, be careful, future Budd).
  * Menu Master:
    * Add new dishes, with descriptions, prices, and categories.
    * Tweak existing menu items.
    * Remove items that are no longer available.
* **Review Regulator:**
  * Read all the reviews.
  * Delete reviews if they're spammy or just plain mean.

## Tech I Used (The Geeky Stuff 💻)

* **Python 3.something:** The brains of the operation.
* **SQLite:** My go-to for a simple, file-based database. No fancy server needed!
* **`rich`:** Makes the command line look *rich* and fancy. Tables, colors, the works.
* **`bcrypt`:** For scrambling passwords so nobody can steal 'em.
* **My Own Validation Magic:** Made sure you can't just type gibberish everywhere.
* **Logging:** Keeps a diary of what's happening in `data/swigato_app.log`, just in case.

## How the Code is Laid Out (My Digital Filing Cabinet 📂)

```text
swigato_project/
├── admin/                  # Where all the admin magic happens
│   ├── __init__.py
│   └── actions.py
├── cart/                   # For your shopping cart stuff
│   ├── __init__.py
│   └── models.py
├── data/                   # Important files live here!
│   ├── swigato.db          # The actual database!
│   └── swigato_app.log     # The app's diary
├── delivery/               # Maybe for drone delivery in v2? (kidding... mostly)
│   ├── __init__.py
│   └── tracker.py
├── orders/                 # All about your food orders
│   ├── __init__.py
│   └── models.py
├── restaurants/            # Restaurant and menu details
│   ├── __init__.py
│   └── models.py
├── reviews/                # What everyone thinks
│   ├── __init__.py
│   └── models.py
├── users/                  # Handles user accounts and logins
│   ├── __init__.py
│   ├── auth.py
│   └── models.py
├── utils/                  # Handy helper scripts
│   ├── __init__.py
│   ├── database.py         # Talks to the SQLite database
│   ├── logger.py           # Sets up the logging
│   └── validation.py       # Makes sure your input is good
├── .gitignore              # Tells Git what to ignore (boring stuff)
├── main.py                 # This is where you run the app!
└── README.md               # You're reading it! Hi!
```

## Wanna Try It? Here's How

1. **Stuff You Need First:**
    * Python (like, version 3-ish).
    * `pip` (it usually comes with Python).

2. **Get the Code (If I Ever Put This on GitHub):**
    If you want to play around with the code, you can clone it from GitHub (or wherever I put it). Here's how:

    ```bash
    git clone https://github.com/Amartya-007/swigato_project 
    cd swigato_project
    ```

    For now, you probably just have the files in a folder.

3. **Install the Goodies:**
    Open your terminal, do `. code` [To Open VS Code you MORON], or just navigate to the project folder, and run this command to install the required libraries:

    ```bash
    pip install rich bcrypt
    ```

4. **Let's Go!**
    Run this command:

    ```bash
    python main.py
    ```

    * Boom! The app should start. If it's the first time, it'll create the `swigato.db` file in the `data/` folder.
    * It also throws in some sample restaurants and menu items so you're not starting with an empty app.
    * And, super important, it makes a default admin user for me.

## Admin Login Deets (Shhh, It's a Secret... Kinda)

When the app starts up for the very first time (or if there are no admins), it creates one for you (me!):

* **Username:** `admin`
* **Password:** `admin123` (I changed it from just 'admin' to make it a *tiny* bit more secure, lol)

Use these to get into the Admin Panel and feel the power!

## No Nonsense Input

I spent a bunch of time making sure the app doesn't crash if you type weird things. It checks if you left something blank, if you typed letters where numbers should be, if your choices are valid, and all that jazz. If you mess up, it'll (hopefully) tell you what you did wrong in a nice way.

---

## Project by Amartya Vishwakarma | 2025
