from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from datetime import datetime 

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

    if request.method == 'POST':
        # Call the buy_cart method to move items from cart to purchases
        purchase_ids = Cart.buy_cart(userid)
        if purchase_ids:
            flash('Successfully Purchased Items. You can view your purchase history in your profile page.')
        else:
            flash('No items in cart to buy in cart or insufficient balance.')
        
        return redirect(url_for('carts.carts'))


    # render the page by adding information to the index.html file
    return render_template('carts.html',
                           ucart=user_cart,
                           total=total_price, 
                           prices = [Product.get(i.pid).price for i in user_cart], 
                           length = len(user_cart),
                           names = [Product.get(i.pid).name for i in user_cart])

