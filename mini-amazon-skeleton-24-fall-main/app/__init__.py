from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .wishlist import bp as wishlist_bp
    app.register_blueprint(wishlist_bp)

    from .productreviewpage import bp as productreviewing_bp
    app.register_blueprint(productreviewing_bp)
    
    from .sellerreviewpage import bp as sellerreviewing_bp
    app.register_blueprint(sellerreviewing_bp)

    from .carts import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .sellerpage import bp as seller_bp
    app.register_blueprint(seller_bp)
    
    from .productpage import bp as product_bp
    app.register_blueprint(product_bp)

    return app