from flask import jsonify, Blueprint

@bp.route('/products')
def product():
    products = Product.get_all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'seller_id': product.seller_id,
        'price': product.price,
        'available': product.available
    }for product in products]) 
@bp.route('/product/<int:id>')
def product():
    product = Product.get(id)
    if product:
        return jsonify({
            id: product.id,
            name: product.name,
            seller_id: product.seller_id,
            price: product.price,
            available: product.available
        })
    return jsonify({'error': 'Product not found'}), 404