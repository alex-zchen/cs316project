from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login



##SKELETON: Used User skeleton from mini amazon project to build user class. Specifically used init for the user and the auth functions. 
class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, balance = 0):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = 0

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
        SELECT password, id, email, firstname, lastname
        FROM Users
        WHERE email = :email
        """, email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
        SELECT email
        FROM Users
        WHERE email = :email
        """,
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
            INSERT INTO Users(email, password, firstname, lastname)
            VALUES(:email, :password, :firstname, :lastname)
            RETURNING id
            """,
            email=email,
            password=generate_password_hash(password),
            firstname=firstname, lastname=lastname)

            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
    @staticmethod
    def update_info(id, email, firstname, lastname, balance):
        try:
            app.db.execute("""
            UPDATE Users
            SET email = :email, firstname = :firstname, lastname = :lastname, balance = :balance
            WHERE id = :id
            """, 
            id=id, email=email, firstname=firstname, lastname=lastname, balance = balance)
            return True
        except Exception as e:
            print(str(e))
            return False

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
        SELECT id, email, firstname, lastname, balance
        FROM Users
        WHERE id = :id
        """,
                              id=id)
        return User(*(rows[0])) if rows else None
