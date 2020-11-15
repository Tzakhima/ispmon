import flask
from flask import request
import redis
import pickle

# Flask Parameters
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Redis
message_r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/metrics', methods=['POST'])
def get_metrics():
    data = request.json
    print(data)
    message_r.lpush('metrics', pickle.dumps(data))
    return '200'


app.run(port=80, host='0.0.0.0')
