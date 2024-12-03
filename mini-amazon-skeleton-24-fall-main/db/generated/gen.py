from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

# Initialize Faker
Faker.seed(0)
fake = Faker()

# Define numbers for entries
num_users = 100
num_categories = 10
num_products = 10000 
num_purchases = 10000
num_reviews = 10000
num_seller_reviews = 10000

# Helper function to write CSV files
def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

# Generate realistic product categories and items
product_categories = [
    ("Electronics", ["Smartphone", "Laptop", "Tablet", "Camera", "Headphones", "Smartwatch"]),
    ("Home & Kitchen", ["Blender", "Vacuum Cleaner", "Air Fryer", "Coffee Maker", "Microwave", "Dishwasher"]),
    ("Sports & Outdoors", ["Bicycle", "Tent", "Backpack", "Hiking Shoes", "Kayak", "Fitness Tracker"]),
    ("Clothing", ["Jacket", "T-Shirt", "Sneakers", "Jeans", "Socks", "Hat"]),
    ("Beauty", ["Lipstick", "Foundation", "Shampoo", "Conditioner", "Moisturizer", "Perfume"]),
]

def generate_image_url(product_name):
    """Simulate a unique image URL using a placeholder service with product-specific formatting."""
    base_url = "https://via.placeholder.com/150?text="
    formatted_name = "+".join(product_name.split())
    return f"{base_url}{formatted_name}"

# Generate Users
def gen_users(num_users):
    rows = []
    for uid in range(1, num_users + 1):
        email = fake.unique.email()
        balance = round(random.uniform(0, 1000), 2)
        password = generate_password_hash("password123")
        address = fake.address().replace("\n", ", ")
        firstname = fake.first_name()
        lastname = fake.last_name()
        rows.append([uid, email, balance, password, address, firstname, lastname])
    return rows

# Generate Categories
def gen_categories():
    rows = []
    for cid, (name, products) in enumerate(product_categories, start=1):
        description = f"A variety of {name.lower()} products"
        rows.append([cid, name, description])
    return rows

# Generate Products
def gen_products(num_products):
    rows = []
    for pid in range(1, num_products + 1):
        category_id, (category, products) = random.choice(list(enumerate(product_categories, start=1)))
        product_name = random.choice(products)
        name = f"{fake.word().capitalize()} {product_name}"
        seller_id = random.randint(1, num_users)
        price = round(random.uniform(5, 500), 2)
        available = random.choice([True, False])
        description = fake.sentence(nb_words=15)
        image_url = generate_image_url(name)
        rows.append([pid, name, seller_id, price, available, description, category_id, image_url])
    return rows

# Generate Purchases with unique, sequential IDs
def gen_purchases(num_purchases):
    rows = []
    for pid in range(1, num_purchases + 1):
        uid = random.randint(1, num_users)
        product_id = random.randint(1, num_products)
        time_purchased = fake.date_time_this_year()
        rows.append([pid, uid, product_id, time_purchased])  # Unique, sequential IDs
    return rows

# Generate Product Reviews
def gen_product_reviews(num_reviews):
    rows = []
    for rid in range(1, num_reviews + 1):
        uid = random.randint(1, num_users)
        product_id = random.randint(1, num_products)
        rscore = random.randint(1, 5)
        time_reviewed = fake.date_time_this_year()
        rows.append([rid, uid, product_id, rscore, time_reviewed, False])
    return rows

# Generate Seller Reviews
def gen_seller_reviews(num_seller_reviews):
    rows = []
    for sid in range(1, num_seller_reviews + 1):
        uid = random.randint(1, num_users)
        seller_id = random.randint(1, num_users)
        rscore = random.randint(1, 5)
        time_reviewed = fake.date_time_this_year()
        rows.append([sid, uid, seller_id, rscore, time_reviewed, True])  # Unique, sequential IDs
    return rows

# Generate data with unique IDs
user_data = gen_users(num_users)
category_data = gen_categories()
product_data = gen_products(num_products)
purchase_data = gen_purchases(num_purchases)
product_review_data = gen_product_reviews(num_reviews)
seller_review_data = gen_seller_reviews(num_seller_reviews)

# Define file paths
base_path = "./"  # Adjust path as necessary
file_paths = {
    "Users.csv": user_data,
    "Categories.csv": category_data,
    "Products.csv": product_data,
    "Purchases.csv": purchase_data,
    "ProductReviews.csv": product_review_data,
    "SellerReviews.csv": seller_review_data,
}

# Write each CSV without headers
for filename, data in file_paths.items():
    with open(base_path + filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)
