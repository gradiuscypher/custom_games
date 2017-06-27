import traceback
import pprint
from flask import Blueprint, request

callback = Blueprint('callback', __name__)


@callback.route('/test', methods=["POST"])
def test():
    try:
        content = request.get_json()
        pprint.pprint(content)
        return "Success", 200
    except:
        print(traceback.format_exc())
