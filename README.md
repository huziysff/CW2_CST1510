# Week 7: Secure Authentication System

**Student Name:** [Muhammad Huzaifa]
**Student ID:** [M01039517]
**Course:** CST1510

## Project Description
A secure authentication system using Python and bcrypt.

## Features
* Password hashing with salts.
* User registration and login (DB-backed using SQLite).
* Streamlit multi-page UI with session-state based login and role handling.

## Run locally
1. Install dependencies:

```
pip install -r requirements.txt
```

2. Initialize DB (optional - `main.py` will run migrations and seed CSVs):

```
python main.py
```

3. Start the Streamlit app (open login page):

```
streamlit run pages/0_home.py
```

Visit the login page and create an account or sign in (e.g., `alice` is a seeded demo user).