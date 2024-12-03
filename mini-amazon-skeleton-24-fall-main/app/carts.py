from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from datetime import datetime 

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart

from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from datetime import datetime
from .models.user import User
from .models.purchase import Purchase
from .models.product import Product
bp = Blueprint('carts', __name__)
coupon = False


class PromoForm(FlaskForm):
    discount = StringField('Coupon Code')
    submit = SubmitField('Update')

@bp.route('/carts', methods=['GET', 'POST'])
def carts():
    # userid
    user_cart = {}
    userid = current_user.id
    # find total price and cart:
    if(current_user.is_authenticated):
        user_cart = Cart.get(userid)
    total_price = Cart.get_total_price(userid)

    # Get coupon discount if any
    discount_info = Cart.get_active_discount(userid)
    discount_percent = discount_info['percent'] if discount_info else None
    discount_amount = (total_price * discount_percent / 100) if discount_percent else 0
    final_total = total_price - discount_amount
    
    if request.method == 'POST':
        # Call the buy_cart method to move items from cart to purchases
        purchase_ids = Cart.buy_cart(userid)
        if purchase_ids:
            flash('Successfully Purchased Items. You can view your purchase history in your profile page.')
        else:
            flash('An error occurred while purchasing items. You might not have enough balance or the products you want to buy might not have enough quantity.')
        
        return redirect(url_for('carts.carts'))


    # render the page by adding information to the index.html file
    return render_template('carts.html',
                           ucart=user_cart,
                           total="{:.2f}".format(total_price), 
                           discount_percent=discount_percent,
                           discount_amount="{:.2f}".format(discount_amount),
                           final_total="{:.2f}".format(final_total),
                           prices = [Product.get(i.pid).price for i in user_cart], 
                           length = len(user_cart),
                           names = [Product.get(i.pid).name for i in user_cart])

@bp.route('/delete/<int:uid>/<int:pid>', methods=['POST'])
def delete(uid, pid):
    # userid
    user_cart = {}
    userid = current_user.id
    # find total price and cart:
    if(current_user.is_authenticated):
        user_cart = Cart.get(userid)
    total_price = Cart.get_total_price(userid)
    if request.method == "POST":
        try:
            Cart.remCart(uid, pid)
            flash("Item Removed Successfully!")
            return redirect(url_for('carts.carts'))
        except:
            flash("Error: Could Not Remove Item From Cart")
            return redirect(url_for('carts.carts'))

@bp.route('/plus/<int:pid>/<int:quant>', methods=['POST'])
def plus(pid, quant):
    try:
        Cart.upQuant(current_user.id, pid, quant)
        return redirect(url_for('carts.carts'))
    except:
        return redirect(url_for('carts.carts'))

@bp.route('/minus/<int:pid>/<int:quant>', methods=['POST'])
def minus(pid, quant):
    try: 
        Cart.lowQuant(current_user.id, pid, quant)
        return redirect(url_for('carts.carts'))
    except:
        return redirect(url_for('carts.carts'))

@bp.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    coupon_code = request.form.get('coupon_code')
    if Cart.apply_coupon(current_user.id, coupon_code):
        flash('Coupon applied successfully!')
    else:
        flash('Invalid coupon code.')
    return redirect(url_for('carts.carts'))

