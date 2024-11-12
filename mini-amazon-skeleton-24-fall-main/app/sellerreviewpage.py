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
from .models.sellerreview import SellerReviewReview
from .models.purchase import Purchase
from datetime import datetime


from flask import Blueprint
bp = Blueprint('sellerreviewpage', __name__)

class SellerReviewForm(FlaskForm):
    seller_name = IntegerField('Seller ID', validators=[DataRequired()])
    rscore = IntegerField('Review Score', validators=[DataRequired()])
    submit = SubmitField('List Review')

class ChangeReviewForm(FlaskForm):
    rscore = IntegerField('Change Score (1-5)', validators=[DataRequired()])

@bp.route('/sellerreviewpage', methods=['GET', 'POST'])
def sellerreviewpagebackend():
    seller_id = request.args.get('seller_id')
    form = SellerReviewForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            if (form.rscore.data>=0 and form.rscore.data<=5) 
                        and (len(SellerReviewReview.check_by_uid_for_sid(current_user.id, form.seller_name.data)) ==0)
                         and (len(Purchase.if_purchased(current_user.id, form.seller_name.data)) !=0):
                if SellerReviewReview.reviewSeller(current_user.id, 
                                form.seller_name.data, form.rscore.data, 
                                datetime.now()):
                    print('Review Successfully Posted!')
                    return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))
            else: 
                print('Review Unsuccessfully Posted!')
                return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))
    # find the products current user has listed:
    if current_user.is_authenticated:
        if seller_id:
            sid = int(seller_id)
            sreviews = SellerReviewReview.get_all_by_uid_for_sid(current_user.id, sid)
        else:
            sreviews = SellerReviewReview.get_all_by_uid(current_user.id)
    else:
        sreviews = None
    # render the page by adding information to the sellerreview.html file
    return render_template('sellerreview.html',
                            sreviews=sreviews,
                            form=form)

@bp.route('/sellerreviewpage/delete/<int:seller_id>', methods=['POST'])
def seller_delete(seller_id):
    if current_user.is_authenticated:
        SellerReviewReview.delete_seller_id(current_user.id, seller_id)
        return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))
    else:
        return jsonfiy({}), 404


@bp.route('/sellerreviewpage/change/<int:seller_id>', methods=['POST'])
def seller_change(seller_id):
    form = ChangeReviewForm()
    if current_user.is_authenticated:
        if (form.rscore.data>=0 and form.rscore.data<=5):
            SellerReviewReview.update_rscore(current_user.id, seller_id, form.rscore.data, datetime.now())
    else:
        return jsonfiy({}), 404
    
    return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))