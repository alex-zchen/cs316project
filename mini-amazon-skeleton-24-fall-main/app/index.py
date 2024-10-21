from flask import render_template, request
from flask_login import current_user
from datetime import datetime
from flask import jsonify
from .models.product import Product
from flask import Blueprint
from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

class PurchaseForm(FlaskForm):
    pid = IntegerField('Product ID (NOT NAME!)', validators=[DataRequired()])
    submit = SubmitField('Purchase!')

@bp.route('/', methods=['GET', 'POST'])
def index():
    seller_id = request.args.get('seller_id')
    top_k = request.args.get('top_k')
    if seller_id and top_k:
        seller_id = int(seller_id)
        top_k = int(top_k)
        products = Product.filter_by(seller_id, top_k)
    elif seller_id:
        seller_id = int(seller_id)
        products = Product.filter_by(seller_id)
    elif top_k:
        top_k = int(top_k)
        products = Product.filter_by(None, top_k)
    else:
        products = Product.get_all(True)

    form = PurchaseForm()
    if form.validate_on_submit():
        if Purchase.add_purchase(
            current_user.id, form.pid.data
        ):
            return redirect(url_for('index.index'))

    # find the products current user has bought:

    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases, form = form)
