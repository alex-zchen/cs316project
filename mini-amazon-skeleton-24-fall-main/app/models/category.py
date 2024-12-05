from flask import current_app as app

class Category:
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    #Get all categories
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT id, name, description
FROM Categories
ORDER BY name
''')
        return [Category(*row) for row in rows]

    #Get a category by ID
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, description
FROM Categories
WHERE id = :id
''',
                            id=id)
        return Category(*(rows[0])) if rows else None

    #Get a category name by ID
    @staticmethod
    def get_name(id):
        category = Category.get(id)
        return category.name if category else "Uncategorized"