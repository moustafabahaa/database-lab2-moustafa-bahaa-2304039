# Lab 2: Login & To-Do Application

## Team
- Moustafa Bahaa, ID: 2304039
- Hassan Ashraf ID: 2304026


## Technology
- Back end: Python 3 + Flask
- Front end: HTML, Bootstrap 5, Jinja templates
- Database: MySQL (plain SQL with PyMySQL, no ORM)

## How to run
1. Install Python 3 and MySQL.
2. Run `pip install -r requirements.txt`
3. Run `database/schema.sql` in MySQL (for example with DBeaver).
4. Copy `.env.example` to `.env` and fill in your MySQL password and a random SECRET_KEY.
5. Run `python app.py`
6. Open http://127.0.0.1:5000

## Features
- R1 Register with validation, "Email Already Exists" message, automatic login
- R2 Login with the same error message for a wrong email or password, logout
- R3 Private list (redirect to the login page if not logged in)
- R4 to R7 Add, edit, mark done, delete (with "Are you sure?" confirmation)
- R8 Server-side validation with the exact messages
- R9 bcrypt hashes, parameterized queries only, user_id comes from the session
- R10 Bootstrap UI, responsive, friendly empty-list message

## Answers
**(a)** UPDATE and DELETE contain `AND user_id = ?` so a user can only change their own to-dos. The to-do id comes from the browser, so anybody can send another user's id. Without the condition, one user could edit or delete other users' to-dos.

**(b)** MySQL refuses the insert with a foreign key error, because that user_id does not exist in the users table. This is the foreign key constraint (referential integrity).

**(c)** If the database is stolen, a hash can't be turned back into the password. bcrypt is salted, so equal passwords give different hashes, and it is slow on purpose to resist guessing attacks.

**(d)** NOT NULL only rejects a missing value. An empty text `''` is a value, so MySQL accepts it. Only our own check can refuse an empty name.