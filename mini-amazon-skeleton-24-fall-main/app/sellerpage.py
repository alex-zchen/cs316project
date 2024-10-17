from flask_login import current_user
from flask import jsonify
from .models.product import Product
from flask import Blueprint
from flask import render_template
from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

bp = Blueprint('sellerpage', __name__)


class ListForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    price = IntegerField('Product Price', validators=[DataRequired()])
    submit = SubmitField('List Item')


@bp.route('/sellerpage', methods=['GET', 'POST'])
def seller():
    # get all available products for sale:
    products_in_inventory = {}
    form = ListForm()
    if form.validate_on_submit():
        if Product.list_product(
            form.product_name.data, current_user.id, form.price.data
        ):
            flash('Product Successfully Listed!')
            return redirect(url_for('sellerpage.seller'))
    # find the products current user has listed:
    if current_user.is_authenticated:
        products_in_inventory = Product.filter_by(
            current_user.id)
    # render the page by adding information to the seller.html file
    return render_template('seller.html',
                       products_in_inventory=products_in_inventory, form = form)
