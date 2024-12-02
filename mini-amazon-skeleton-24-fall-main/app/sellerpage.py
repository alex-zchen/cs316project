from flask_login import current_user
from flask import jsonify
from .models.product import Product
from .models.purchase import Purchase
from .models.category import Category
from flask import Blueprint
from flask import render_template
from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

bp = Blueprint('sellerpage', __name__)


class ListForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    price = IntegerField('Product Price', validators=[DataRequired()])
    description = TextAreaField('Product Description')
    category_id = SelectField('Category', coerce=int)
    image_url = StringField('Image URL')
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=1)
    submit = SubmitField('List Item')


@bp.route('/sellerpage', methods=['GET', 'POST'])
def seller():
    form = ListForm()
    
    # Populate category choices
    categories = Category.get_all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    view_type = request.args.get('view', 'current')  # 'current' or 'sold'
    
    if form.validate_on_submit():
        if Product.list_product(
            form.product_name.data, current_user.id, form.price.data
        ):
            flash("Product listed successfully!")
            return redirect(url_for('sellerpage.seller'))
        else: 
            flash("Error listing product: Quantity or Price cannot be negative")
    
    products = []
    if current_user.is_authenticated:
        if view_type == 'sold':
            # Get sold products with fulfillment status, purchase time, and purchase ID
            products = Purchase.get_seller_sold_products(current_user.id)
        else:
            # Get current listings
            products = Product.filter_by(current_user.id)
    
    page_size = 5 
    product_pages = []

    for i in range(0, len(products), page_size):
        page = products[i:i + page_size]
        product_pages.append(page)
    
    if len(product_pages) == 0:
        product_pages = [[]]

    return render_template('seller.html',
                         products_in_inventory=product_pages,
                         form=form,
                         view_type=view_type) 