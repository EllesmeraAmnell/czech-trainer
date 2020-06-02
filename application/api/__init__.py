from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api_bp', __name__, url_prefix='/api')
api = Api(blueprint)

from . import routes
