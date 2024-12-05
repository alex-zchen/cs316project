from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask import current_app as app
from flask_wtf import FlaskForm
from flask_login import current_user, login_required
import math
from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart
from .models.productreview import AllReviews
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from datetime import datetime
from .models.category import Category

bp = Blueprint('products', __name__)

#Form to take in review score to be posted
class ProductReviewForm(FlaskForm):
    rscore = IntegerField('Review Score (1-5)', validators=[DataRequired()])
    submit = SubmitField('List Review')

#Form to take in new review score to be posted
class ChangeReviewForm(FlaskForm):
    rscore = IntegerField('Change Score (1-5)', validators=[DataRequired()])
    submit = SubmitField('List Review')

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

    # Get filtered products based on given criteria
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


@bp.route('/products/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.get(product_id)
    if product is None:
        abort(404)
    
    # Get all sellers for this product
    sellers = Product.get_sellers(product_id)
    
    # Get all reviews for this product
    reviews = AllReviews.get_product_reviews(product_id)
    
    form = None
    purchased = False
    
    #If a user has logged in and purchased a displayed product, allow them to review it or edit their reviews
    if current_user.is_authenticated:
        purchase_check = Purchase.if_purchased_item(current_user.id, product_id)
        purchased = purchase_check is not None
        
        if purchased:
            existing_review = AllReviews.check_by_uid_for_pid(current_user.id, product_id)
            if existing_review:
                form = ChangeReviewForm()
            else:
                form = ProductReviewForm()
                
            if form.validate_on_submit():
                rscore = form.rscore.data
                if 1 <= rscore <= 5:
                    try:
                        if existing_review:
                            AllReviews.update_rscore(
                                current_user.id,
                                product_id,
                                rscore,
                                datetime.now()
                            )
                            flash('Review updated successfully!', 'success')
                        else:
                            AllReviews.reviewProduct(
                                current_user.id,
                                product_id,
                                rscore,
                                datetime.now()
                            )
                            flash('Review added successfully!', 'success')
                        return redirect(url_for('products.product_detail', product_id=product_id))
                    except Exception as e:
                        flash('Error submitting review: ' + str(e), 'error')
                else:
                    flash('Review score must be between 1 and 5', 'error')
    
    return render_template('product_detail.html',
                         product=product,
                         sellers=sellers,
                         reviews=reviews,
                         purchased=purchased,
                         form=form,
                         Category=Category)


#Allow users to update their cart
@bp.route('/products/<int:product_id>/add_to_cart', methods=['POST'])
@login_required
def add_to_cart(product_id):
    seller_id = request.args.get('seller_id', type=int)
    quantity = request.form.get('quantity', type=int, default=1)
    
    if not seller_id or not quantity:
        flash('Invalid request', 'error')
        return redirect(url_for('products.product_detail', product_id=product_id))
    
    Cart.addCart(current_user.id, product_id, quantity, seller_id)
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))

#Allow users to delete their reviews
@bp.route('/products/<int:product_id>/delete_review', methods=['POST'])
@login_required
def delete_review(product_id):
    try:
        # Delete the review
        AllReviews.delete_product_id(current_user.id, product_id)
        flash('Review deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting review: ' + str(e), 'error')
    
    return redirect(url_for('products.product_detail', product_id=product_id))


