from flask import Blueprint, render_template, request, abort
from flask import current_app as app
from flask_login import current_user
import math
from .models.product import Product

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET', 'POST'])
def product_list():
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 4

    # Get filtered products
    products = Product.search_and_filter(
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

    # Get total count for pagination
    total_products = Product.get_filtered_count(search_query)
    total_pages = math.ceil(total_products / per_page)

    return render_template('products.html',
                         products=products,
                         page=page,
                         total_pages=total_pages,
                         search_query=search_query,
                         sort_by=sort_by,
                         sort_order=sort_order)

@bp.route('/products/<int:product_id>')  # Changed from /product to /products
def product_detail(product_id):
    product = Product.get(product_id)
    if product is None:
        abort(404)

        
    return render_template('product_detail.html', product=product)

