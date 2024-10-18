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
from .models.sellerreview import SellerReview

from humanize import naturaltime
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

from flask import Blueprint
bp = Blueprint('sellerreviewpage', __name__)

class ReviewForm(FlaskForm):
    rscore = IntegerField('Review Score', validators=[DataRequired()])
    submit = SubmitField('List Review')

@bp.route('/sellerreviewpage', methods=['GET', 'POST'])
def sellerreview():
    seller_id = request.args.get('seller_id')
    form = ReviewForm()
    if form.validate_on_submit():
        if (form.rscore.data>=0 and form.rscore.data<=5) and
                    SellerReview.find_seller(seller_id):
            if SellerReview.reviewSeller(current_user.id, 
                            form.seller_name.data, form.rscore.data, 
                            datetime.datetime.now()):
                flash('Review Successfully Posted!')
                return redirect(url_for('sellerreviewpage.sellerreview'))
        else: 
            flash('Review Unsuccessfully Posted!')
            return redirect(url_for('sellerreviewpage.sellerreview'))
    # find the products current user has listed:
    if current_user.is_authenticated:
        if seller_id:
            sid = int(seller_id)
            sreviews = SellerReview.get_all_by_uid_sid(current_user.id, sid)
        else:
            sreviews = SellerReview.get_all_by_uid_since(current_user.id, 
                                datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        sreviews = None
    # render the page by adding information to the sellerreview.html file
    return render_template('sellerreview.html',
                            sreviews=sreviews,
                            humanize_time=humanize_time)


@bp.route('/sellerreviewpage/summary', methods=['GET'])
def sellerreview_add(seller_id):
    if current_user.is_authenticated:
        ids = SellerReview.reviewSeller(
            current_user.id, seller_id, datetime.datetime.now())
        return redirect(url_for('wishlist.wishlist'))
    else:
        return jsonfiy({}), 404