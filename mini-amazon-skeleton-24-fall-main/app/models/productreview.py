from flask import current_app as app


class ProductReview:
    def __init__(self, id, uid, pid, rscore, time_reviewed):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.rscore= rscore
        self.time_reviewed = time_reviewed

    @staticmethod
    def get(id):
        rows = app.db.execute("""
SELECT id, uid, pid, rscore, time_reviewed
FROM ProductReveiws
WHERE id = :id
""",
                              id=id)
        return ProductReview(*(rows[0])) if rows else None

    @staticmethod
    def reviewItem(uid, pid, rscore, time_reviewed):
        try:
            rows = app.db.execute("""
INSERT INTO ProductReviews(uid, pid, rscore, time_reviewed)
VALUES(:uid, :pid, :rscore, :time_reviewed)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid,
                                  rscore=rscore
                                  time_reviewed=time_reveiwed)
            id = rows[0][0]
            return ProductReview.get(id)
        except Exception as e:
            # likely item already reviewed; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed
FROM ProductReviews
WHERE uid = :uid
AND time_reviewed >= :since
ORDER BY time_reviewed DESC
''',
                              uid=uid,
                              since=since)
        return [ProductReview(*row) for row in rows]


    @staticmethod
    def get_all_by_pid_since(pid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, rscore, time_reviewed
FROM ProductReviews
WHERE pid = :pid
AND time_reviewed >= :since
ORDER BY time_reivewed DESC
''',
                              pid=pid,
                              since=since)
        return [ProductReview(*row) for row in rows]