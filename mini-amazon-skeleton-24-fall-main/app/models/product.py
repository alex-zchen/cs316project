from flask import current_app as app


class Product:
    #Initialize product object
    def __init__(self, id, name, seller_id, price, available, description=None, category_id=None, image_url=None, avg_rating=None, review_count=None, quantity=None):
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
        self.quantity = quantity

    #Get a product by ID
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
       COALESCE(r.review_count, 0) as review_count,
       COALESCE(p.quantity, 0) as quantity
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
WHERE p.id = :id
''',
                            id=id)
        return Product(*(rows[0])) if rows is not None else None

    #Get all products
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

    #Get all products by seller ID
    @staticmethod 
    def filter_by(seller_id, k = 10000):
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
       COALESCE(r.review_count, 0) as review_count,
       p.quantity
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
       COALESCE(r.review_count, 0) as review_count,
       p.quantity
FROM Products p
LEFT JOIN avg_ratings r ON p.id = r.pid
ORDER BY p.price DESC
LIMIT :k
''',
                                k=k)
            return [Product(*row) for row in rows]

    @staticmethod
    def search_and_filter(search_query, sort_by, sort_order, category, page, per_page):
        query = '''
            WITH avg_ratings AS (
                SELECT pid, 
                       COALESCE(AVG(rscore)::NUMERIC(10,1), 0) as avg_rating,
                       COUNT(*) as review_count
                FROM ProductReviews
                WHERE for_seller = FALSE
                GROUP BY pid
            )
            SELECT p.id, 
                   p.name, 
                   p.seller_id, 
                   COALESCE(p.price, 0) as price, 
                   COALESCE(p.available, false) as available, 
                   p.description, 
                   p.category_id, 
                   p.image_url,
                   COALESCE(r.avg_rating, 0) as avg_rating,
                   COALESCE(r.review_count, 0) as review_count,
                   COALESCE(p.quantity, 0) as quantity
            FROM Products p
            LEFT JOIN avg_ratings r ON p.id = r.pid
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE p.available = TRUE
            AND COALESCE(p.quantity, 0) > 0
        '''
        params = {}

        if search_query:
            query += ' AND (LOWER(p.name) LIKE LOWER(:search) OR LOWER(COALESCE(p.description, \'\')) LIKE LOWER(:search))'
            params['search'] = f'%{search_query}%'

        if category and category != 'all':
            query += ' AND p.category_id = :category'
            params['category'] = category

        # Add sorting
        if sort_by == 'price':
            query += f' ORDER BY price {sort_order}'
        elif sort_by == 'rating':
            query += f' ORDER BY avg_rating {sort_order}'
        else:
            query += f' ORDER BY avg_rating {sort_order}'

        # Add pagination
        query += ' LIMIT :per_page OFFSET :offset'
        params['per_page'] = per_page
        params['offset'] = (page - 1) * per_page

        rows = app.db.execute(query, **params)
        return [Product(*row) for row in rows]

    #Get the count of all products
    @staticmethod
    def get_filtered_count(search_query, category=None):
        query = '''
            SELECT COUNT(*)
            FROM Products p
            WHERE p.available = TRUE
            AND COALESCE(p.quantity, 0) > 0
        '''
        params = {}

        if search_query:
            query += ' AND (LOWER(name) LIKE LOWER(:search) OR LOWER(description) LIKE LOWER(:search))'
            params['search'] = f'%{search_query}%'

        if category and category != 'all':
            query += ' AND category_id = :category'
            params['category'] = category

        count = app.db.execute(query, **params)
        return count[0][0]

    #List a product
    @staticmethod
    def list_product(name, seller_id, price, description=None, category_id=None, image_url=None, quantity=1):
        try:
            if quantity < 0:
                return None
            
            if price < 0:
                return None
            
            # Check if product already exists for this seller
            existing = app.db.execute("""
SELECT id FROM Products 
WHERE name = :name AND seller_id = :seller_id
""",
                                    name=name,
                                    seller_id=seller_id)
            
            if existing:
                return None  # Product already exists for this seller
            
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

    #Return list of categories
    @staticmethod
    def get_all_categories():
        rows = app.db.execute('''
            SELECT DISTINCT c.id, c.name
            FROM Products p
            JOIN Categories c ON p.category_id = c.id
            WHERE p.category_id IS NOT NULL
            ORDER BY c.name
        ''')
        return [(row[0], row[1]) for row in rows]  # Returns tuples of (id, name)

    #Get the count of each product under specific criteria
    @staticmethod
    def get_filtered_count(search_query, category=None):
        query = 'SELECT COUNT(*) FROM Products WHERE 1=1'
        params = {}

        if search_query:
            query += ' AND (LOWER(name) LIKE LOWER(:search) OR LOWER(description) LIKE LOWER(:search))'
            params['search'] = f'%{search_query}%'

        if category and category != 'all':
            query += ' AND category_id = :category'
            params['category'] = category

        count = app.db.execute(query, **params)
        return count[0][0]

    #Get all sellers that have a given pid for sale
    @staticmethod
    def get_sellers(product_id):
        rows = app.db.execute('''
            WITH original_product AS (
                SELECT name, seller_id as original_seller_id
                FROM Products 
                WHERE id = :product_id
            )
            SELECT p.id, p.seller_id, p.price, p.quantity,
                   (p.seller_id = op.original_seller_id) as is_original_seller
            FROM Products p
            JOIN original_product op ON p.name = op.name
            WHERE p.available = TRUE
            AND p.quantity > 0
            ORDER BY is_original_seller DESC, p.price ASC
        ''', product_id=product_id)
        return rows