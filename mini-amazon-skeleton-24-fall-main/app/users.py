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

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UpdateInfoForm(FlaskForm):
    email = StringField('Email')
    address = StringField('Address')
    password = PasswordField('Password')
    fname = StringField('First Name')
    lname = StringField('Last Name')
    balance = DecimalField('Balance')
    submit = SubmitField('Update!')

@bp.route('/editInfo', methods = ["GET", "POST"])
def editInfo():
    form = UpdateInfoForm()
    return render_template('changeUserDetailForm.html', form = form)

@bp.route('/updateInfo', methods = ["GET", "POST"])
def updateInfo():
    try:
        fname = request.form.get('fname')
    except:
        fname = None
    try:
        lname = request.form.get('lname')
    except:
        lname = None
    try:
        email = request.form.get('email')
    except:
        email = None
    try:
        address = request.form.get('address')
    except:
        address = None
    try:
        password = request.form.get('password')
    except:
        password = None

    try:
        balance = request.form.get('balance')
    except:
        balance = None

    current_user.firstname = fname if fname else current_user.firstname
    current_user.lastname = lname if lname else current_user.lastname
    current_user.email = email if email else current_user.email
    current_user.password = password if password else current_user.password
    current_user.address = address if address else current_user.address
    current_user.balance = balance if balance else current_user.balance
    current_user.update_info(id = current_user.id, email = current_user.email, firstname = current_user.firstname, lastname = current_user.lastname, balance = current_user.balance, password = current_user.password, address = current_user.address)
    login()
    user = current_user
    purchases = Purchase.get_all_by_uid_since(uid = user.id, since = -1)
    print(user.id)
    productPurchases = []
    #Loading purchases in
    for i, purchase in enumerate(purchases):
        product = Product.get(purchase.pid)
        purchaseObj = {}
        purchaseObj['PurchaseDate'] = purchase.time_purchased
        purchaseObj["ProductName"] = product.name
        purchaseObj['Amount Paid'] = product.price
        purchaseObj['Fulfillment Status'] = "Not yet shipped" if not purchase.fulfilled else "Shipped"
        productPurchases.append(purchaseObj)


    page_size = 5 
    productPurchasePages = []

    for i in range(0, len(productPurchases), page_size):
        page = productPurchases[i:i + page_size]
        productPurchasePages.append(page)
    
    print(productPurchasePages)
    if(len(productPurchasePages) == 0):
        productPurchasePages = [[]]

    return render_template('profile.html', user = current_user, purchases = productPurchasePages)

@bp.route("/profile", methods=["GET"]) 
def profileDisplay():
    user = current_user
    purchases = Purchase.get_all_by_uid_since(uid = user.id, since = -1)
    
    # Group purchases by timestamp
    orders = {}
    for purchase in purchases:
        product = Product.get(purchase.pid)
        timestamp = purchase.time_purchased
        
        if timestamp not in orders:
            orders[timestamp] = {
                'total': 0,
                'count': 0,
                'timestamp': timestamp,
                'uid': user.id
            }
        
        orders[timestamp]['total'] += float(product.price)
        orders[timestamp]['count'] += 1
    
    # Convert to list and sort by timestamp
    order_list = list(orders.values())
    order_list.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Paginate orders
    page_size = 5 
    order_pages = []
    for i in range(0, len(order_list), page_size):
        page = order_list[i:i + page_size]
        order_pages.append(page)
    
    if len(order_pages) == 0:
        order_pages = [[]]

    return render_template('profile.html', user=user, orders=order_pages)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.product_list'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('products.product_list')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)



@bp.route('/public_profile/<int:user_id>', methods=['GET'])
def pubPage(user_id):
    #Get user by ID
    user = User.get(user_id)
    return render_template('publicpage.html', user=user)

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products.product_list'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(email = form.email.data,
                         password = form.password.data,
                         firstname = form.firstname.data,
                         lastname = form.lastname.data, address = form.address.data, balance = 0):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('products.product_list'))


@bp.route('/userpage')
def user_page():
    return redirect(url_for('userpage.html'))

@bp.route('/updateBalanceOnPurchase', methods = ["GET", "POST"])
def update_balance_on_purchase():
    requestedChange = request.get('balanceChange')
    if(current_user.balance >= balanceChange):
        current_user.balance = current_user.balance - balanceChange
        current_user.update_info(id = current_user.id, email = current_user.email, firstname = current_user.firstname, lastname = current_user.lastname, balance = current_user.balance, password = current_user.password, address = current_user.address)
        return True
    else:
        return False

@bp.route("/order/<uid>/<timestamp>", methods=["GET"]) 
def order_page(uid, timestamp):
    purchases = Purchase.get_orders_by_time(uid=uid, timestamp=timestamp)
    productPurchases = []
    
    for purchase in purchases:
        product = Product.get(purchase.pid)
        purchaseObj = {}
        purchaseObj['PurchaseDate'] = purchase.time_purchased
        purchaseObj["ProductName"] = product.name
        purchaseObj['Amount_Paid'] = "{:.2f}".format(float(product.price))
        purchaseObj['Fulfillment_Status'] = "Not yet shipped" if not purchase.fulfilled else "Shipped"
        productPurchases.append(purchaseObj)

    return render_template('order.html', 
                         purchases=productPurchases, 
                         timestamp=timestamp, 
                         uid=uid)