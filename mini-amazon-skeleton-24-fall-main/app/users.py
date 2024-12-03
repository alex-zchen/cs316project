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
import base64
import io
import matplotlib
import matplotlib.pyplot as plt
from flask import current_app as app

from flask import Blueprint
bp = Blueprint('users', __name__)


#Form for logging users in, including email, password and remember me option. Inspired by mini amazon skeleton.
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#Update info form for users to change log in info, includes validation and password hashing, and when submitted replaces user data in db
#and logs them back in. 
class UpdateInfoForm(FlaskForm):
    email = StringField('Email')
    address = StringField('Address')
    password = PasswordField('Password')
    fname = StringField('First Name')
    lname = StringField('Last Name')
    balance = DecimalField('Balance')
    submit = SubmitField('Update!')

#This router displays the edit info form and calls update info on submit.
@bp.route('/editInfo', methods = ["GET", "POST"])
def editInfo():
    form = UpdateInfoForm()
    return render_template('changeUserDetailForm.html', form = form)

#Evidently, this gets the relevant updated fields, then passes them to the user model to update the user in the db. It relogs them in,
#so current user is accurately updated (in accordance with the new DB object), and reloads their profile page.
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
    
    # Group purchases by timestamp
    orders = {}
    cumulative_total = 0
    for purchase in reversed(purchases):
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
        cumulative_total += float(product.price)
        print(cumulative_total)
        orders[timestamp]['cumulative_total'] = cumulative_total
    
    # Convert to list and sort by timestamp
    order_list = list(orders.values())
    order_list.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Create graph data object to show cumulative spend
    graph_data = {
        'x': [order['timestamp'] for order in order_list],
        'y': [order['cumulative_total'] for order in order_list]
    }
    
    #Generate and save a base64 encoded graph of the cumulative spend over time
    plt.figure(figsize=(10, 5))
    plt.plot(graph_data['x'], graph_data['y'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Spent ($)')
    plt.title('Cumulative Purchases')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    # Paginate orders with page size of 5
    page_size = 5 
    order_pages = []
    for i in range(0, len(order_list), page_size):
        page = order_list[i:i + page_size]
        order_pages.append(page)
    
    if len(order_pages) == 0:
        order_pages = [[]]

    return render_template('profile.html', user=user, orders=order_pages, graph_data=graph_base64)

@bp.route("/profile", methods=["GET"]) 
#Displays the profile page, showing their info (editable) and their previous purchases in reverse chronological order.
def profileDisplay():
    user = current_user
    purchases = Purchase.get_all_by_uid_since(uid=user.id, since=-1)
    
    # Group purchases by timestamp
    orders = {}
    cumulative_total = 0
    for purchase in reversed(purchases):
        product = Product.get(purchase.pid)
        timestamp = purchase.time_purchased
        
        if timestamp not in orders:
            orders[timestamp] = {
                'total': 0,
                'count': 0,
                'timestamp': timestamp,
                'uid': user.id
            }
        
        # Calculate price after coupon discount if applicable
        price = float(product.price)
        if purchase.coupon_code:
            discount = app.db.execute('''
                SELECT discount_percent
                FROM Coupons
                WHERE code = :code
            ''', code=purchase.coupon_code)[0][0]
            price = price * (1 - float(discount)/100)
        
        orders[timestamp]['total'] += price * purchase.quantity
        orders[timestamp]['count'] += purchase.quantity
        cumulative_total += price * purchase.quantity
        orders[timestamp]['cumulative_total'] = cumulative_total
    
    # Convert to list and sort by timestamp
    order_list = list(orders.values())
    order_list.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Create graph data object to show cumulative spend
    graph_data = {
        'x': [order['timestamp'] for order in order_list],
        'y': [order['cumulative_total'] for order in order_list]
    }
    
    #Generate and save a base64 encoded graph of the cumulative spend over time
    plt.figure(figsize=(10, 5))
    plt.plot(graph_data['x'], graph_data['y'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Spent ($)')
    plt.title('We go above and beyond to make your account history transparent. \n Here is a graph of your cumulative spend over time.')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    # Paginate orders with page size of 5
    page_size = 5 
    order_pages = []
    for i in range(0, len(order_list), page_size):
        page = order_list[i:i + page_size]
        order_pages.append(page)
    
    if len(order_pages) == 0:
        order_pages = [[]]

    return render_template('profile.html', user=user, orders=order_pages, graph_data=graph_base64)

#Log the user in by validating their email using password hashing (inspired by mini amazon skeleton).
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

#Display public profile page for users using their publicly shown info, including seller-specific info. 
@bp.route('/public_profile/<int:user_id>', methods=['GET'])
def pubPage(user_id):
    #Get user by ID
    user = User.get(user_id)
    return render_template('publicpage.html', user=user)

#New form for registering new users, inspired by mini amazon skeleton. Validates all fields and checks that email is unique.
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


#Registers new user with form data from registration form. 
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

#Logs user out using the flask login logout function.
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('products.product_list'))


#Ensures that user has enough balance before completing a purchase, updates balance and returns true if successful. 
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
        price = float(product.price)
        
        # Apply coupon discount if applicable
        if purchase.coupon_code:
            discount = app.db.execute('''
                SELECT discount_percent
                FROM Coupons
                WHERE code = :code
            ''', code=purchase.coupon_code)[0][0]
            price = price * (1 - float(discount)/100)
        
        purchaseObj = {}
        purchaseObj['PurchaseDate'] = purchase.time_purchased
        purchaseObj["ProductName"] = product.name
        purchaseObj['Quantity'] = purchase.quantity
        purchaseObj['Amount_Paid'] = "{:.2f}".format(price * purchase.quantity)
        purchaseObj['Fulfillment_Status'] = "Not yet shipped" if not purchase.fulfilled else "Shipped"
        productPurchases.append(purchaseObj)

    return render_template('order.html', 
                         purchases=productPurchases, 
                         timestamp=timestamp, 
                         uid=uid)