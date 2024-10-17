from flask import jsonify, Blueprint, request
from .models.product import Product

bp = Blueprint('products', __name__)

@bp.route('/products')
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

# You can remove the separate top_expensive route as it's now handled in listproduct