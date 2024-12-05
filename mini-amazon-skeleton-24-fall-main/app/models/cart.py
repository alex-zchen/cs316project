from flask import current_app as app
from flask_login import current_user
from datetime import datetime 

class Cart:
    
    def __init__(self, id, uid, pid, quant, seller_id):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.quant = quant
        self.seller_id = seller_id

    # Returns array of all cart items
    @staticmethod
    def get(uid):
        rows = app.db.execute('''
        SELECT id, uid, pid, quant, seller_id
        FROM Carts
        WHERE uid = :uid
        ''',
        uid=uid)
        if len(rows) > 0: 
            return [Cart(*row) for row in rows]
        else: 
            return {}

    # Checks if cart is empty
    @staticmethod
    def isEmpty(uid):
        if Cart.get(current_user.id) == {}:
            return True
        else: return False
    
    # Sums price of all products in cart
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
            return rows[0][0]
    
    # Adds item to cart
    @staticmethod
    def addCart(uid, pid, quant, seller_id):
        try:
            # Check if item already exists in cart from this seller
            existing_item = app.db.execute("""
                SELECT id, quant
                FROM Carts
                WHERE uid = :uid AND pid = :pid AND seller_id = :seller_id
            """,
            uid=uid, pid=pid, seller_id=seller_id)
            
            if existing_item:
                # Update quantity if item exists
                app.db.execute("""
                UPDATE Carts
                SET quant = quant + :quant
                WHERE uid = :uid AND pid = :pid AND seller_id = :seller_id
                """,
                uid=uid, pid=pid, quant=quant, seller_id=seller_id)
            else:
                # Insert new item if it doesn't exist
                app.db.execute("""
                INSERT INTO Carts(uid, pid, quant, seller_id)
                VALUES(:uid, :pid, :quant, :seller_id)
                """,
                uid=uid, pid=pid, quant=quant, seller_id=seller_id)
            
            return Cart.get(uid)
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return None
    
    # Removes item from cart
    @staticmethod
    def remCart(uid, pid):
        rows = app.db.execute("""
        DELETE 
        FROM Carts c
        WHERE c.uid = :uid AND c.pid = :pid
        """,
        uid=uid, pid=pid)
        return Cart.get

    # Increases quantity of item
    @staticmethod
    def upQuant(uid, pid, quant):
        rows = app.db.execute("""
                UPDATE Carts
                SET quant = quant + 1
                WHERE uid = :uid AND pid = :pid
                """,
                uid=uid, pid=pid, quant=quant)
        return None
    
    # Decreases quantity of item
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

    # Applies coupon code to cart total price
    @staticmethod
    def apply_coupon(uid, code):
        try:
            # Check if coupon exists and get discount
            coupon = app.db.execute('''
                SELECT discount_percent
                FROM Coupons
                WHERE code = :code
            ''', code=code)
            
            if not coupon:
                return False
            
            # Store the active coupon for the user
            app.db.execute('''
                UPDATE Users
                SET active_coupon = :code
                WHERE id = :uid
            ''', code=code, uid=uid)
            
            return True
        except Exception as e:
            print(f"Error applying coupon: {e}")
            return False

    # Checks active discounts
    @staticmethod
    def get_active_discount(uid):
        try:
            result = app.db.execute('''
                SELECT c.discount_percent
                FROM Users u
                JOIN Coupons c ON u.active_coupon = c.code
                WHERE u.id = :uid
            ''', uid=uid)
            
            if result:
                return {'percent': result[0][0]}
            return None
        except Exception as e:
            print(f"Error getting discount: {e}")
            return None

    # Buys cart, removes items from cart and adds to purchases
    @staticmethod
    def buy_cart(uid):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Get total price and apply discount
            total_price = Cart.get_total_price(uid)
            if total_price == 0:
                return None
            
            # Get active coupon if any
            active_coupon = app.db.execute('''
                SELECT active_coupon
                FROM Users
                WHERE id = :uid
            ''', uid=uid)
            coupon_code = active_coupon[0][0] if active_coupon and active_coupon[0][0] else None
            
            discount_info = Cart.get_active_discount(uid)
            if discount_info:
                total_price = total_price * (1 - discount_info['percent'] / 100)
            
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
                return None

            # If balance is sufficient and quantities are available, proceed with purchase
            rows = app.db.execute("""
                INSERT INTO Purchases (uid, pid, time_purchased, quantity, coupon_code)
                SELECT uid, pid, :time_purchased, quant, :coupon_code
                FROM Carts
                WHERE uid = :uid
                RETURNING id
            """, 
            uid=uid,
            time_purchased=current_time,
            coupon_code=coupon_code)

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

                # Clear the user's active coupon after purchase
                app.db.execute("""
                    UPDATE Users 
                    SET active_coupon = NULL
                    WHERE id = :uid
                """,
                uid=uid)

                # Return the IDs of the purchases made
                return [row[0] for row in rows]

            return None

        except Exception as e:
            print(f"Error moving cart to purchases: {e}")
            return None

        


