from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask import current_app as app
from flask_login import current_user, login_required
import math
from .models.product import Product
from .models.cart import Cart
from .models.category import Category

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET', 'POST'])
def product_list():
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'desc')
    category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 4

    # Get all available categories for the dropdown
    categories = Product.get_all_categories()

    # Get filtered products
    products = Product.search_and_filter(
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        category=category,
        page=page,
        per_page=per_page
    )

    # Get total count for pagination
    total_products = Product.get_filtered_count(search_query, category)
    total_pages = math.ceil(total_products / per_page)

    return render_template('products.html',
                         products=products,
                         page=page,
                         total_pages=total_pages,
                         search_query=search_query,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         category=category,
                         categories=categories)

@bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.get(product_id)
    if product is None:
        abort(404)
        
    return render_template('product_detail.html', 
                         product=product,
                         Category=Category)

@bp.route('/products/<int:product_id>/add_to_cart', methods=['POST'])
@login_required
def add_to_cart(product_id):
    Cart.addCart(current_user.id, product_id, 1)
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))


