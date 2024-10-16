from flask import current_app as app
from datetime import datetime

now = str(datetime.now())

class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since = -1):
        if(since != -1):
            rows = app.db.execute('''
            SELECT id, uid, pid, time_purchased
            FROM Purchases
            WHERE uid = :uid
            AND time_purchased >= :since
            ORDER BY time_purchased DESC
            ''',
            uid=uid,
            since=since)
        else:
            rows = app.db.execute('''
            SELECT id, uid, pid, time_purchased
            FROM Purchases
            WHERE uid = :uid
            ORDER BY time_purchased DESC
            ''',
            uid=uid)
        return [Purchase(*row) for row in rows]
    @staticmethod
    def add_purchase(uid, pid): #IN THE FUTURE SHOULD THROW ERROR IF PURCHASE IS NOT IN TABLE
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            rows = app.db.execute("""
INSERT INTO Purchases(uid, pid, time_purchased)
VALUES(:uid, :pid, :time_purchased)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid, 
                                    time_purchased = current_time)
            id = rows[0][0]
            return Purchase.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
