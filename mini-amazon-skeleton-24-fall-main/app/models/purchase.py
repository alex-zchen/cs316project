from flask import current_app as app
from datetime import datetime

now = str(datetime.now())

class Purchase:
    def __init__(self, id, uid, pid, time_purchased, fulfilled):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.fulfilled = fulfilled

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, fulfilled
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since = -1):
        if(since != -1):
            rows = app.db.execute('''
            SELECT id, uid, pid, time_purchased, fulfilled
            FROM Purchases
            WHERE uid = :uid
            AND time_purchased >= :since
            ORDER BY time_purchased DESC
            ''',
            uid=uid,
            since=since)
        else:
            rows = app.db.execute('''
            SELECT id, uid, pid, time_purchased, fulfilled
            FROM Purchases
            WHERE uid = :uid
            ORDER BY time_purchased DESC
            ''',
            uid=uid)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def if_purchased(uid, sid):
        rows = app.db.execute('''
            SELECT Purchases.id, uid, pid, time_purchased, fulfilled
            FROM Purchases, Products
            WHERE Purchases.uid = :uid
            AND Purchases.pid = Products.id
            AND Products.seller_id = :sid
            ORDER BY time_purchased DESC
            ''',
            uid=uid,
            sid=sid)
        return [Purchase(*(rows[0]))]  if rows else None
      
    @staticmethod
    def add_purchase(uid, pid):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            rows = app.db.execute("""
INSERT INTO Purchases(uid, pid, time_purchased, fulfilled)
VALUES(:uid, :pid, :time_purchased, FALSE)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid, 
                                  time_purchased=current_time)
            id = rows[0][0]
            return Purchase.get(id)
        except Exception as e:
            print(str(e))
            return None
    @staticmethod
    def get_seller_sold_products(seller_id):
        rows = app.db.execute('''
        SELECT p.id, p.name, p.price, pu.uid as buyer_id, pu.time_purchased, pu.id as purchase_id, pu.fulfilled
        FROM Products p
        JOIN Purchases pu ON p.id = pu.pid
        WHERE p.seller_id = :seller_id
        ORDER BY pu.time_purchased DESC
        ''', seller_id=seller_id)
        return rows 