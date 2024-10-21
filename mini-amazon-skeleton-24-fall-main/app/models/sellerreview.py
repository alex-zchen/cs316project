from flask import current_app as app


class SellerReviewReview:
    def __init__(self, id, uid, sid, rscore, time_reviewed, for_seller):
        self.id = id
        self.uid = uid
        self.sid = sid
        self.rscore= rscore
        self.time_reviewed = time_reviewed
        self.for_seller = for_seller

    @staticmethod
    def get(id):
        rows = app.db.execute("""
SELECT id, uid, sid, rscore, time_reviewed, for_seller
FROM SellerReviews
WHERE id = :id
""",
                              id=id)
        return SellerReviewReview(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, sid, rscore, time_reviewed, for_seller
FROM SellerReviews
WHERE uid = :uid
ORDER BY time_reviewed DESC
''',
                              uid=uid)
        return [SellerReviewReview(*row) for row in rows] 

    @staticmethod
    def get_all_by_uid_for_sid(uid, sid):
        rows = app.db.execute('''
SELECT SellerReviews.id, uid, sid, rscore, time_reviewed, for_seller
FROM SellerReviews
WHERE uid = :uid
AND sid = :sid
AND for_seller = TRUE
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              sid=sid)
        return [SellerReviewReview(*row) for row in rows] 

    @staticmethod
    def check_by_uid_for_sid(uid, sid):
        rows = app.db.execute('''
SELECT 1
FROM SellerReviews
WHERE uid = :uid
AND sid = :sid
AND for_seller = TRUE
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              sid=sid)
        return rows if rows is not None else None

    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
SELECT id, uid, sid, rscore, time_reviewed, for_seller
FROM SellerReviews
WHERE sid = :sid
AND for_seller = TRUE
ORDER BY time_reivewed DESC
''',
                              sid=sid)
        return [SellerReviewReview(*row) for row in rows] 

    @staticmethod
    def get_all_by_product_id(sid):
        rows = app.db.execute('''
SELECT SellerReviews.id, uid, Products.id, rscore, time_reviewed, for_seller
FROM SellerReviews, Products
WHERE sid = :sid
AND Products.seller_id = :sid
AND for_seller = TRUE
ORDER BY time_reivewed DESC
''',
                              sid=sid)
        return [SellerReviewReview(*row) for row in rows] 

    @staticmethod
    def reviewSeller(uid, sid, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO SellerReviews(uid, sid, rscore, time_reviewed, for_seller)
VALUES(:uid, :sid, :rscore, :time_reviewed, :for_seller)
RETURNING id
""",
                                  uid=uid,
                                  sid = sid,
                                  rscore=rscore,
                                  time_reviewed=time_reviewed,
                                  for_seller='true')
            id = rows[0][0]
            return SellerReviewReview.get(id)
        except Exception as e:
            # likely item already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def delete_seller_id(uid, sid):
        rows = app.db.execute('''
DELETE FROM SellerReviews
WHERE sid = :sid
AND uid = :uid
''',
                              uid=uid,
                              sid=sid)

    @staticmethod
    def update_rscore(uid, sid, rscore, time_reviewed):
        rows = app.db.execute('''
UPDATE SellerReviews
SET rscore = :rscore, time_reviewed = :time_reviewed
WHERE sid = :sid
AND uid = :uid
''',
                              uid=uid,
                              sid=sid,
                              rscore=rscore,
                              time_reviewed=time_reviewed)