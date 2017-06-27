from flask import Blueprint

callback = Blueprint('callback', __name__)


@callback.route('/test')
def test():
    return 'Success', 200
