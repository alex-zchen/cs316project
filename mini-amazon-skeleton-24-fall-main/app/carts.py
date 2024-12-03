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
    global coupon
    form = PromoForm()
    user_cart = {}
    userid = current_user.id
    # find total price and cart:
    if(current_user.is_authenticated):
        user_cart = Cart.get(userid)
    total_price = Cart.get_total_price(userid)
    if(coupon == True):
        total_price= float(total_price) - float(0.1) * float(total_price)

    if request.method == 'POST':
        # Call the buy_cart method to move items from cart to purchases
        purchase_ids = Cart.buy_cart(userid)
        if purchase_ids:
            coupon = False
            Cart.remove_promo()
            flash('Successfully Purchased Items. You can view your purchase history in your profile page.')
        else:
            flash('An error occurred while purchasing items. You might not have enough balance or the products you want to buy might not have enough quantity.')
        
        return redirect(url_for('carts.carts'))


    # render the page by adding information to the index.html file
    return render_template('carts.html',
                           ucart=user_cart,
                           total="{:.2f}".format(total_price), 
                           prices = [Product.get(i.pid).price for i in user_cart], 
                           length = len(user_cart),
                           names = [Product.get(i.pid).name for i in user_cart],
                           form = form)

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

@bp.route('/coupon', methods=['POST'])
def coupon():
    global coupon
    if(request.form.get('discount') == 'HAPPY'):
        coupon = True
        Cart.use_promo()
        flash("Promo Code Successful!")
    else:
        flash("Promo code not valid")
    return redirect(url_for('carts.carts'))