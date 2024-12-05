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

#old version of sellerpage instead user.py pubPag

#for input and button field of making first review
class SellerReviewForm(FlaskForm):
    seller_name = IntegerField('Seller ID', validators=[DataRequired()])
    rscore = IntegerField('Review Score', validators=[DataRequired()])
    submit = SubmitField('List Review')

#for input chaging already made review
class ChangeReviewForm(FlaskForm):
    rscore = IntegerField('Change Score (1-5)', validators=[DataRequired()])

#old version of reviewpage made by seller
@bp.route('/sellerreviewpage', methods=['GET', 'POST'])
def sellerreviewpagebackend():
    seller_id = request.args.get('seller_id')
    form = SellerReviewForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            if (form.rscore.data>=0 and form.rscore.data<=5) and (len(SellerReviewReview.check_by_uid_for_sid(current_user.id, form.seller_name.data)) ==0) and (len(Purchase.if_purchased(current_user.id, form.seller_name.data)) !=0):
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

    if(sreviews): #Pagination for seller reviews, acting weird with redisplay though.
        page_size = 5 
        sreviewsPages = []

        for i in range(0, len(sreviews), page_size):
            page = sreviews[i:i + page_size]
            sreviewsPages.append(page)
        
        print(sreviewsPages)
    else:
        sreviewsPages = [[]]
        

    return render_template('sellerreview.html',
                            sreviews=sreviewsPages,
                            form=form)

#still used
#delete seller reivew
@bp.route('/sellerreviewpage/delete/<int:seller_id>', methods=['POST'])
def seller_delete(seller_id):
    if current_user.is_authenticated:
        SellerReviewReview.delete_seller_id(current_user.id, seller_id)
        return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))
    else:
        return jsonfiy({}), 404

#still used
#change seller reivew
@bp.route('/sellerreviewpage/change/<int:seller_id>', methods=['POST'])
def seller_change(seller_id):
    form = ChangeReviewForm()
    if current_user.is_authenticated:
        if (form.rscore.data>=0 and form.rscore.data<=5):
            SellerReviewReview.update_rscore(current_user.id, seller_id, form.rscore.data, datetime.now())
    else:
        return jsonfiy({}), 404
    
    return redirect(url_for('sellerreviewpage.sellerreviewpagebackend'))

# Add new route for handling reviews from public page:
@bp.route('/seller_review_from_public/<int:seller_id>', methods=['POST'])
def seller_review_from_public(seller_id):
    if not current_user.is_authenticated:
        flash('Please log in to leave a review.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
        
    # Verify purchase
    if not Purchase.if_purchased(current_user.id, seller_id):
        flash('You must purchase from this seller before leaving a review.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
    
    # Get review score from form
    rscore = request.form.get('rscore')
    if not rscore or not (0 <= int(rscore) <= 5):
        flash('Please provide a valid rating between 0 and 5.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
    
    # Check if review already exists
    existing_review = SellerReviewReview.check_by_uid_for_sid(current_user.id, seller_id)
    if existing_review:
        flash('You have already reviewed this seller.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
    
    # Add the review
    if SellerReviewReview.reviewSeller(current_user.id, seller_id, int(rscore), datetime.now()):
        flash('Review successfully posted!')
    else:
        flash('Error posting review.')
    
    return redirect(url_for('users.pubPage', user_id=seller_id))

#most recent on public page
#delete seller review
@bp.route('/seller_delete_from_public/<int:seller_id>', methods=['POST'])
def seller_delete_from_public(seller_id):
    if current_user.is_authenticated:
        SellerReviewReview.delete_seller_id(current_user.id, seller_id)
        flash('Review deleted successfully!')
    return redirect(url_for('users.pubPage', user_id=seller_id))

#most recent on public page
#change seller review
@bp.route('/seller_change_from_public/<int:seller_id>', methods=['POST'])
def seller_change_from_public(seller_id):
    if not current_user.is_authenticated:
        flash('Please log in to update your review.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
    
    rscore = request.form.get('rscore')
    if not rscore or not (1 <= int(rscore) <= 5):
        flash('Please provide a valid rating between 1 and 5.')
        return redirect(url_for('users.pubPage', user_id=seller_id))
    
    SellerReviewReview.update_rscore(current_user.id, seller_id, int(rscore), datetime.now())
    flash('Review updated successfully!')
    return redirect(url_for('users.pubPage', user_id=seller_id))