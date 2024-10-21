from flask import current_app as app
from flask_login import current_user
from datetime import datetime 

class Cart:
    def __init__(self, id, uid, pid, quant):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.quant = quant

    @staticmethod
    def get(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Carts
        WHERE uid = :uid
        ''',
        uid=uid)
        if len(rows) > 0: 
            return Cart(*(rows[0])) 
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
            SELECT SUM(c.quant * p.price) AS total_price
            FROM Carts c
            JOIN Products p ON c.pid = p.id
            WHERE c.uid = c.uid;
            """,
            uid=uid)
        return rows

    @staticmethod
    def buy_cart(uid):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Step 1: Insert items from Cart to Purchases
            rows = app.db.execute("""
                INSERT INTO Purchases (uid, pid, time_purchased)
                SELECT uid, pid, :time_purchased
                FROM Carts
                WHERE uid = :uid
                RETURNING id
            """, 
            uid=uid,
            time_purchased=current_time)

            # Check if any items were moved
            if not rows:
                return None
            app.db.execute("""
                DELETE FROM Carts
                WHERE uid = :uid
            """, 
            uid=uid)
            
            # Return the IDs of the purchases made
            purchase_ids = [row[0] for row in rows]
            return purchase_ids

        except Exception as e:
            # Handle any exceptions that occur and print the error for debugging
            print(f"Error moving cart to purchases: {e}")
            return None

        


