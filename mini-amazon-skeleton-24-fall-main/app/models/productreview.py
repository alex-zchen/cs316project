from flask import current_app as app


class AllReviews:
    def __init__(self, id, uid, pid, rscore, time_reviewed, for_seller):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.rscore= rscore
        self.time_reviewed = time_reviewed
        self.for_seller = for_seller

    @staticmethod
    def get(id):
        rows = app.db.execute("""
SELECT id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReveiws
WHERE id = :id
""",
                              id=id)
        return ProductReview(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, seller_id, rscore, time_reviewed, for_seller
FROM ProductReviews
WHERE uid = :uid
ORDER BY time_reviewed DESC
''',
                              uid=uid)
        return [ProductReview(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_for_sid(uid, seller_id):
        rows = app.db.execute('''
SELECT ProductReviews.id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews, Products
WHERE uid = :uid
AND seller_id = :seller_id
AND for_seller = TRUE
ORDER BY time_reivewed DESC
''',
                              uid = uid
                              seller_id=seller_id)
        return [ProductReview(*row) for row in rows] if rows is not None else None

    @staticmethod
    def get_all_by_pid(pid):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews
WHERE pid = :pid
AND for_seller = FALSE
ORDER BY time_reivewed DESC
''',
                              pid=pid)
        return [ProductReview(*row) for row in rows]

    @staticmethod
    def get_all_by_seller_id(seller_id):
        rows = app.db.execute('''
SELECT ProductReviews.id, uid, seller_id, rscore, time_reviewed, for_seller
FROM ProductReviews, Products
WHERE pid = Products.id
AND seller_id = :seller_id
AND for_seller = TRUE
ORDER BY time_reivewed DESC
''',
                              seller_id=seller_id)
        return [ProductReview(*row) for row in rows]

    @staticmethod
    def reviewItem(uid, pid, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO ProductReviews(uid, pid, rscore, time_reviewed, for_seller)
VALUES(:uid, :pid, :rscore, :time_reviewed, :for_seller)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid,
                                  rscore=rscore,
                                  time_reviewed=time_reveiwed,
                                  for_seller='false')
            id = rows[0][0]
            return ProductReview.get(id)
        except Exception as e:
            # likely item already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def reviewSeller(uid, seller_id, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO ProductReviews(uid, pid, rscore, time_reviewed, for_seller)
SELECT :uid, id, :rscore, :time_reviewed, :for_seller
FROM Products
WHERE seller_id = :seller_id
LIMIT 1
RETURNING id
""",
                                  uid=uid,
                                  seller_id = seller_id,
                                  rscore=rscore,
                                  time_reviewed=time_reveiwed,
                                  for_seller='true')
            id = rows[0][0]
            return ProductReview.get(id)
        except Exception as e:
            # likely item already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None