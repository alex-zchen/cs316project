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
        return rows[0][0]
    
    @staticmethod
    def addCart(uid, pid, quant):
        rows = app.db.execute("""
        INSERT INTO Carts(uid, pid, quant)
        VALUES(:uid, :pid, :quant)
        RETURNING id
        """,
        uid=uid, pid=pid, quant=1)
        return Cart.get
            

