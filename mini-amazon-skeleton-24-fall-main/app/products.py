from flask import jsonify, Blueprint, request, redirect, url_for, flash
from .models.product import Product
from flask_login import login_required, current_user
from .models.cart import Cart

bp = Blueprint('products', __name__)

@bp.route('/products')
# all the products from all the sellers
def listproduct():
    seller_id = request.args.get('seller_id', type=int)
    top_k = request.args.get('top_k', type=int)

    if seller_id:
        products = Product.get_seller_all(seller_id)
    else:
        products = Product.get_all()

    if top_k:
        products = sorted(products, key=lambda x: x.price, reverse=True)[:top_k]

    return jsonify([{
        'id': product.id,
        'name': product.name,
        'seller_id': product.seller_id,
        'price': product.price,
        'available': product.available
    } for product in products])
#products with a specific id
@bp.route('/product/<int:id>')
def searchproduct(id):
    product = Product.get(id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'seller_id': product.seller_id,
            'price': product.price,
            'available': product.available
        })
    return jsonify({'error': 'Product not found'}), 404

