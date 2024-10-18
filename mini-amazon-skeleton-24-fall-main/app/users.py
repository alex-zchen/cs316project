from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UpdateInfoForm(FlaskForm):
    email = StringField('Email')
    address = StringField('Password')
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
    return render_template('profile.html', user = current_user)

@bp.route("/profile", methods=["GET"]) 
def profileDisplay():
    user = current_user
    return render_template('profile.html', user=user)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


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
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data, address = form.address.data, balance = 0):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


@bp.route('/userpage')
def user_page():
    return redirect(url_for('userpage.html'))