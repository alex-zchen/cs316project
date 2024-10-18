from flask import current_app as app


class SellerReview:
    def __init__(self, id, uid, sid, rscore, time_reviewed):
        self.id = id
        self.uid = uid
        self.sid = sid
        self.rscore= rscore
        self.time_reviewed = time_reviewed

    @staticmethod
    def get(id):
        rows = app.db.execute("""
SELECT id, uid, sid, rscore, time_reviewed
FROM ProductReveiws
WHERE id = :id
""",
                              id=id)
        return SellerReview(*(rows[0])) if rows else None

    @staticmethod 
    def find_seller(seller_id):
        rows = app.db.execute('''
SELECT id
FROM Products
WHERE seller_id = :seller_id
''',
                              seller_id=seller_id)
        if rows is not None return True
        else return False

    @staticmethod
    def reviewSeller(uid, sid, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO SellerReviews(uid, sid, rscore, time_reviewed)
VALUES(:uid, :sid, :rscore, :time_reviewed)
RETURNING id
""",
                                  uid=uid,
                                  sid=sid,
                                  rscore=rscore
                                  time_reviewed=time_reveiwed)
            id = rows[0][0]
            return SellerReview.get(id)
        except Exception as e:
            # likely seller already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, sid, rscore, time_reviewed
FROM SellerReviews
WHERE uid = :uid
AND time_reviewed >= :since
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              since=since)
        return [SellerReview(*row) for row in rows]

    @staticmethod 
    def get_all_by_uid_sid(uid, sid):
        rows = app.db.execute('''
SELECT id, uid, sid, rscore, time_reviewed
FROM SellerReviews
WHERE sid = :sid
ORDER BY time_reivewed DESC
''',
                              seller_id=seller_id)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_all_by_sid_since(sid, since):
        rows = app.db.execute('''
SELECT id, uid, sid, rscore, time_reviewed
FROM SellerReviews
WHERE sid = :sid
AND time_reviewed >= :since
ORDER BY time_reivewed DESC
''',
                              sid=sid,
                              since=since)
        return [SellerReview(*row) for row in rows]