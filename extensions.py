from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_talisman import Talisman
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
