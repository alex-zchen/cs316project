from flask import current_app as app
from flask_login import current_user

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
        if Cart.get(current_user.id) is {}:
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

