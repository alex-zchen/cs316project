from flask import jsonify
from flask import redirect, url_for
from flask_login import current_user
import datetime

from .models.wishlist import WishlistItem

from flask import Blueprint
bp = Blueprint('wishlist', __name__)


@bp.route('/wishlist')
def wishlist():
    # find the products current user has wishlist:
    if current_user.is_authenticated:
        items = WishlistItem.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        return jsonify([item.__dict__ for item in items])
    else:
        return jsonfiy({}), 404

@bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    if current_user.is_authenticated:
        ids = WishlistItem.wishlistItem(
            current_user.id, product_id, datetime.datetime.now())
        return redirect(url_for('wishlist.wishlist'))
    else:
        return jsonfiy({}), 404