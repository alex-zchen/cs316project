from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('carts', __name__)


@bp.route('/carts', methods=['GET', 'POST'])
def carts():
    # userid
    user_cart = {}
    userid = current_user.id
    # find total price and cart:
    if(current_user.is_authenticated):
        user_cart = Cart.get(userid)
    total_price = Cart.get_total_price(userid)
    # render the page by adding information to the index.html file
    return render_template('carts.html',
                           ucart=user_cart,
                           total=total_price)
