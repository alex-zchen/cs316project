from flask import current_app as app


class Product:
    def __init__(self, id, name, seller_id, price, available, description=None, category_id=None, image_url=None, avg_rating=None, review_count=None):
        self.id = id
        self.name = name
        self.seller_id = seller_id
        self.price = price
        self.available = available
        self.description = description
        self.category_id = category_id
        self.image_url = image_url
        self.avg_rating = avg_rating
        self.review_count = review_count

    @staticmethod
    def get(id):
        rows = app.db.execute('''
WITH avg_ratings AS (
    SELECT pid, 
           AVG(rscore)::NUMERIC(10,1) as avg_rating,
           COUNT(*) as review_count
    FROM ProductReviews
    WHERE for_seller = FALSE
    GROUP BY pid
)
SELECT p.id, p.name, p.seller_id, p.price, p.available, 
       p.description, p.category_id, p.image_url,
       COALESCE(r.avg_rating, 0) as avg_rating,
       COALESCE(r.review_count, 0) as review_count
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
WHERE p.id = :id
''',
                            id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
WITH avg_ratings AS (
    SELECT pid, 
           AVG(rscore)::NUMERIC(10,1) as avg_rating,
           COUNT(*) as review_count
    FROM ProductReviews
    WHERE for_seller = FALSE
    GROUP BY pid
)
SELECT p.id, p.name, p.seller_id, p.price, p.available, 
       p.description, p.category_id, p.image_url,
       COALESCE(r.avg_rating, 0) as avg_rating,
       COALESCE(r.review_count, 0) as review_count
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
WHERE p.available = :available
''',
                            available=available)
        return [Product(*row) for row in rows]

    @staticmethod 
    def filter_by(seller_id, k = 100):
        if seller_id:
            rows = app.db.execute('''

WITH avg_ratings AS (
    SELECT pid, 
           AVG(rscore)::NUMERIC(10,1) as avg_rating,
           COUNT(*) as review_count
    FROM ProductReviews
    WHERE for_seller = FALSE
    GROUP BY pid
)
SELECT p.id, p.name, p.seller_id, p.price, p.available, 
       p.description, p.category_id, p.image_url,
       COALESCE(r.avg_rating, 0) as avg_rating,
       COALESCE(r.review_count, 0) as review_count
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
WHERE p.seller_id = :seller_id
ORDER BY p.price DESC
LIMIT :k
''',
                                seller_id=seller_id,
                                k=k)
            return [Product(*row) for row in rows] if rows is not None else None
        else:
            rows = app.db.execute('''
WITH avg_ratings AS (
    SELECT pid, 
           AVG(rscore)::NUMERIC(10,1) as avg_rating,
           COUNT(*) as review_count
    FROM ProductReviews
    WHERE for_seller = FALSE
    GROUP BY pid
)
SELECT p.id, p.name, p.seller_id, p.price, p.available, 
       p.description, p.category_id, p.image_url,
       COALESCE(r.avg_rating, 0) as avg_rating,
       COALESCE(r.review_count, 0) as review_count
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
ORDER BY p.price DESC
LIMIT :k
''',
                                k=k)
            return [Product(*row) for row in rows]

    @staticmethod
    def search_and_filter(search_query=None, sort_by='id', sort_order='desc', page=1, per_page=4):
        # Base query with ratings
        query = '''
            WITH avg_ratings AS (
                SELECT pid, 
                       AVG(rscore)::NUMERIC(10,1) as avg_rating,
                       COUNT(*) as review_count
                FROM ProductReviews
                WHERE for_seller = FALSE
                GROUP BY pid
            )
            SELECT p.id, p.name, p.seller_id, p.price, p.available, 
                   p.description, p.category_id, p.image_url,
                   COALESCE(r.avg_rating, 0) as avg_rating,
                   COALESCE(r.review_count, 0) as review_count
            FROM Products p
            LEFT JOIN avg_ratings r ON p.id = r.pid
            WHERE p.available = TRUE
        '''

        # Add search conditions if search query exists
        if search_query:
            query += '''
                AND (
                    p.id::text = :search
                    OR p.name ILIKE :search_like
                    OR p.description ILIKE :search_like
                )
            '''
            rows = app.db.execute(query,
                                search=search_query,
                                search_like=f'%{search_query}%',
                                limit=per_page,
                                offset=(page - 1) * per_page)
        else:
            # Add sorting
            if sort_by == 'price' and sort_order in ['asc', 'desc']:
                query += f' ORDER BY p.price {sort_order.upper()}'
            elif sort_by == 'rating' and sort_order in ['asc', 'desc']:
                query += f' ORDER BY avg_rating {sort_order.upper()} NULLS LAST'
            else:
                query += f' ORDER BY p.id {sort_order.upper()}'

            # Add pagination
            query += ' LIMIT :limit OFFSET :offset'
            
            rows = app.db.execute(query,
                                limit=per_page,
                                offset=(page - 1) * per_page)

        return [Product(*row) for row in rows]


    @staticmethod
    def get_filtered_count(search_query=None):
        query = '''
            SELECT COUNT(*)
            FROM Products p
            WHERE available = TRUE
        '''

        if search_query:
            query += '''
                AND (
                    p.id::text = :search
                    OR p.name ILIKE :search_like
                    OR p.description ILIKE :search_like
                )
            '''
            rows = app.db.execute(query,
                                search=search_query,
                                search_like=f'%{search_query}%')
        else:
            rows = app.db.execute(query)

        return rows[0][0] if rows is not None else 0

    @staticmethod
    def list_product(name, seller_id, price, description=None, category_id=None, image_url=None, quantity=1):
        try:
            if quantity < 0:
                return None
            
            if price < 0:
                return None
            
            rows = app.db.execute("""
INSERT INTO Products(name, seller_id, price, available, description, category_id, image_url, quantity)
VALUES(:name, :seller_id, :price, :available, :description, :category_id, :image_url, :quantity)
RETURNING id
""",
                                    name=name,
                                    seller_id=seller_id, 
                                    price=price, 
                                    available='true',
                                    description=description,
                                    category_id=category_id,
                                    image_url=image_url,
                                    quantity=quantity)
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            print(str(e))
            return None