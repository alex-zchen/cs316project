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
from .models.productreview import AllReviews
from datetime import datetime


from flask import Blueprint
bp = Blueprint('productreviewpage', __name__)

#old version instead productpage.py

#form for making first product review
class ProductReviewForm(FlaskForm):
    product_name = IntegerField('Product ID', validators=[DataRequired()])
    rscore = IntegerField('Review Score (1-5)', validators=[DataRequired()])
    submit = SubmitField('List Review')

#form for changing product review
class ChangeReviewForm(FlaskForm):
    rscore = IntegerField('Change Score (1-5)', validators=[DataRequired()])

#old version
#get all product reviews and handles buttons
@bp.route('/productreviewpage', methods=['GET', 'POST'])
def productreviewpagebackend():
    product_id = request.args.get('product_id')
    form = ProductReviewForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            #check if between 1 and 5 or if already made review
            if (form.rscore.data>=0 and form.rscore.data<=5) and (len(AllReviews.check_by_uid_for_pid(current_user.id, form.product_name.data)) ==0):
                if AllReviews.reviewProduct(current_user.id, 
                                form.product_name.data, form.rscore.data, 
                                datetime.now()):
                    print('Review Successfully Posted!')
                    return redirect(url_for('productreviewpage.productreviewpagebackend'))
            else: 
                print('Review Unsuccessfully Posted!')
                return redirect(url_for('productreviewpage.productreviewpagebackend'))
    # find the products current user has listed:
    if current_user.is_authenticated:
        if product_id:
            pid = int(product_id)
            previews = AllReviews.get_all_by_uid_for_pid(current_user.id, pid)
        else:
            previews = AllReviews.get_all_by_uid(current_user.id)
    else:
        previews = None
    previewsPages = []
    page_size = 5

    for i in range(0, len(previews), page_size):
        page = previews[i:i + page_size]
        previewsPages.append(page)
    
    print(previewsPages)
    if(len(previewsPages) == 0):
        previewsPages = [[]]

    # render the page by adding information to the sellerreview.html file
    return render_template('productreview.html',
                            previews=previewsPages,
                            form=form)

#still used
#delete product review
@bp.route('/productreviewpage/delete/<int:product_id>', methods=['POST'])
def product_delete(product_id):
    if current_user.is_authenticated:
        AllReviews.delete_product_id(current_user.id, product_id)
        return redirect(url_for('productreviewpage.productreviewpagebackend'))
    else:
        return jsonfiy({}), 404

#still used
#change a product review
@bp.route('/productreviewpage/change/<int:product_id>', methods=['POST'])
def product_change(product_id):
    form = ChangeReviewForm()
    if current_user.is_authenticated:
        if (form.rscore.data>=0 and form.rscore.data<=5):
            AllReviews.update_rscore(current_user.id, product_id, form.rscore.data, datetime.now())
    else:
        return jsonfiy({}), 404
    
    return redirect(url_for('users.user_reviews'))