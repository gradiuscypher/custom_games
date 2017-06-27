#!/usr/bin/env python

from flask import Flask
from views.callback import callback


# Create the Flask app
app = Flask(__name__)

# Register Blueprint views
app.register_blueprint(callback, url_prefix='/callback')

# Start the Flask app if script is executed
if __name__ == '__main__':
    app.run(debug=True)
