from flask import Flask
from keyvaluestore import KeyValueStore

api = Flask(__name__)


@api.route('/api/v1/images')
def hello():
    with KeyValueStore() as kv:
        return api.response_class(
        response=kv['images'],
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    api.run()
