from flask import current_app as app


class Product:
    def __init__(self, id, name, seller_id, price, available):
        self.id = id
        self.name = name
        self.seller_id = seller_id
        self.price = price
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, seller_id, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, seller_id, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]

    @staticmethod 
    def get_seller_all(seller_id):
        rows = app.db.execute('''
SELECT id, name, seller_id, price, available
FROM Products
WHERE seller_id = :seller_id
''',
                              seller_id=seller_id)
        return [Product(*row) for row in rows]

