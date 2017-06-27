#!/usr/bin/env python

import argparse
from flask import Flask
from views.callback import callback


# Create the Flask app
app = Flask(__name__)

# Register Blueprint views
app.register_blueprint(callback, url_prefix='/callback')

# Start the Flask app if script is executed
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tournament Callback API")
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    if args.dev:
        app.run(debug=True)
    else:
        app.run(host="0.0.0.0", port=80, debug=True)
