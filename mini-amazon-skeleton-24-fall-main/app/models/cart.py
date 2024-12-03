from flask import current_app as app
from flask_login import current_user
from datetime import datetime 

promo = False
class Cart:
    
    def __init__(self, id, uid, pid, quant):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.quant = quant
        self.promo = False

    @staticmethod
    def get(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Carts
        WHERE uid = :uid
        ''',
        uid=uid)
        if len(rows) > 0: 
            return [Cart(*row) for row in rows]
        else: 
            return {}

    @staticmethod
    def isEmpty(uid):
        if Cart.get(current_user.id) == {}:
            return True
        else: return False
    
    @staticmethod
    def get_total_price(uid):
        if Cart.isEmpty(current_user.id) == True:
            return 0
        else:
            rows = app.db.execute("""
            SELECT SUM(c.quant * p.price)
            FROM Carts c
            JOIN Products p ON c.pid = p.id
            WHERE c.uid = :uid;
            """,
            uid=uid)
            if(promo == True):
                return (rows[0][0]) - (0.1)*(rows[0][0])
            return rows[0][0]
    
    @staticmethod
    def addCart(uid, pid, quant):
        try:
            # Check if item already exists in cart
            existing_item = app.db.execute("""
                SELECT id, quant
                FROM Carts
                WHERE uid = :uid AND pid = :pid
            """,
            uid=uid, pid=pid)
            
            if existing_item:
                # Update quantity if item exists
                app.db.execute("""
                UPDATE Carts
                SET quant = quant + :quant
                WHERE uid = :uid AND pid = :pid
                """,
                uid=uid, pid=pid, quant=quant)
            else:
                # Insert new item if it doesn't exist
                app.db.execute("""
                INSERT INTO Carts(uid, pid, quant)
                VALUES(:uid, :pid, :quant)
                """,
                uid=uid, pid=pid, quant=quant)
            
            return Cart.get(uid)
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return None
    
    @staticmethod
    def remCart(uid, pid):
        rows = app.db.execute("""
        DELETE 
        FROM Carts c
        WHERE c.uid = :uid AND c.pid = :pid
        """,
        uid=uid, pid=pid)
        return Cart.get

    @staticmethod
    def upQuant(uid, pid, quant):
        rows = app.db.execute("""
                UPDATE Carts
                SET quant = quant + 1
                WHERE uid = :uid AND pid = :pid
                """,
                uid=uid, pid=pid, quant=quant)
        return None
    
    @staticmethod
    def lowQuant(uid, pid, quant):
        if(quant>1):
            try:
                rows = app.db.execute("""
                UPDATE Carts
                SET quant = quant -1
                WHERE uid = :uid AND pid = :pid
                """,
                uid=uid, pid=pid, quant=quant)
            except:
                flash("Error: Could not decrease quantity")
        return None

    @staticmethod
    def use_promo():
        promo = True
    
    @staticmethod
    def remove_promo():
        promo = False

    @staticmethod
    def get_promo():
        return promo

    @staticmethod
    def buy_cart(uid):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # First check if user has enough balance
            total_price = Cart.get_total_price(uid)
            if(promo):
                total_price = total_price - ((0.1)*total_price)
                promo = False
            if total_price == 0:
                return None
            
            if current_user.balance < total_price:
                return None

            # Check if all products have sufficient quantity
            insufficient_quantity = app.db.execute("""
                SELECT *
                FROM Carts c, Products p
                WHERE c.uid = :uid 
                AND c.pid = p.id 
                AND p.quantity < c.quant
            """, uid=uid)

            if insufficient_quantity:
                # There are items with insufficient quantity
                return None

            # If balance is sufficient and quantities are available, proceed with purchase
            rows = app.db.execute("""
                INSERT INTO Purchases (uid, pid, time_purchased, quantity)
                SELECT uid, pid, :time_purchased, quant
                FROM Carts
                WHERE uid = :uid
                RETURNING id
            """, 
            uid=uid,
            time_purchased=current_time)

            # Update user balance and clear cart only if purchase was successful
            if rows:
                # Update user balance
                new_balance = current_user.balance - total_price
                current_user.update_info(
                    id=current_user.id,
                    email=current_user.email,
                    firstname=current_user.firstname,
                    lastname=current_user.lastname,
                    balance=new_balance,
                    password=current_user.password,
                    address=current_user.address
                )

                # Update product quantities
                app.db.execute("""
                    UPDATE Products p
                    SET quantity = p.quantity - c.quant
                    FROM Carts c
                    WHERE p.id = c.pid AND c.uid = :uid
                """,
                uid=uid)

                # Remove items from cart
                app.db.execute("""
                    DELETE FROM Carts
                    WHERE uid = :uid
                """, 
                uid=uid)

                # Return the IDs of the purchases made
                return [row[0] for row in rows]

            return None

        except Exception as e:
            print(f"Error moving cart to purchases: {e}")
            return None

        


