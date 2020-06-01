from flask import Blueprint
from flask_restplus import Resource, Api

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint)


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
