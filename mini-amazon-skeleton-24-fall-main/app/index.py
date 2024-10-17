from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
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
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)
