import os
from flask import Flask, make_response, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello():
    return make_response(open('%s/templates/index.html' % BASE_DIR).read())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
