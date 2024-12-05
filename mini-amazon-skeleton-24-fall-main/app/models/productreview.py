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
FROM ProductReviews
WHERE id = :id
""",
                              id=id)
        return AllReviews(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews
WHERE uid = :uid
ORDER BY time_reviewed DESC
''',
                              uid=uid)
        return [AllReviews(*row) for row in rows] 

    @staticmethod
    def get_all_by_uid_for_sid(uid, seller_id):
        rows = app.db.execute('''
SELECT ProductReviews.id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews, Products
WHERE uid = :uid
AND pid = Products.id
AND seller_id = :seller_id
AND for_seller = TRUE
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              seller_id=seller_id)
        return [AllReviews(*row) for row in rows] 

    @staticmethod
    def get_all_by_uid_for_pid(uid, pid):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews
WHERE uid = :uid
AND pid = :pid
AND for_seller = FALSE
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              pid=pid)
        return [AllReviews(*row) for row in rows] 

    @staticmethod
    def check_by_uid_for_pid(uid, pid):
        rows = app.db.execute('''
SELECT 1
FROM ProductReviews
WHERE uid = :uid
AND pid = :pid
AND for_seller = FALSE
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              pid=pid)
        return rows if rows is not None else None

    @staticmethod
    def get_all_by_pid(pid):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed, for_seller
FROM ProductReviews
WHERE pid = :pid
AND for_seller = FALSE
ORDER BY time_reviewed DESC
''',
                              pid=pid)
        return [AllReviews(*row) for row in rows] 

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
        return [AllReviews(*row) for row in rows] 

    @staticmethod
    def reviewProduct(uid, pid, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO ProductReviews(uid, pid, rscore, time_reviewed, for_seller)
VALUES(:uid, :pid, :rscore, :time_reviewed, :for_seller)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid,
                                  rscore=rscore,
                                  time_reviewed=time_reviewed,
                                  for_seller='false')
            id = rows[0][0]
            return AllReviews.get(id)
        except Exception as e:
            # likely item already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def delete_product_id(uid, pid):
        rows = app.db.execute('''
DELETE FROM ProductReviews
WHERE pid = :pid
AND uid = :uid
''',
                              uid=uid,
                              pid=pid)

    @staticmethod
    def update_rscore(uid, pid, rscore, time_reviewed):
        rows = app.db.execute('''
UPDATE ProductReviews
SET rscore = :rscore, time_reviewed = :time_reviewed
WHERE pid = :pid
AND uid = :uid
''',
                              uid=uid,
                              pid=pid,
                              rscore=rscore,
                              time_reviewed=time_reviewed)

    @staticmethod
    def get_product_reviews(pid):
        rows = app.db.execute('''
            SELECT pr.uid, pr.pid, pr.rscore, pr.time_reviewed, u.firstname, u.lastname
            FROM ProductReviews pr
            JOIN Users u ON pr.uid = u.id
            WHERE pr.pid = :pid
            AND pr.for_seller = FALSE
            ORDER BY pr.time_reviewed DESC
        ''',
        pid=pid)
        return rows