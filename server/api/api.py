import flask
from flask import request
import redis
import pickle
import json

# Flask Parameters
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Redis
message_r = redis.Redis(host='127.0.0.1', port=6379, db=0)
message_g = redis.Redis(host='127.0.0.1', port=6379, db=1)


@app.route('/metrics', methods=['POST'])
def get_metrics():
    data = request.json
    print(data)
    print("Length: " + str(request.content_length) + " IP: " + str(request.remote_addr))
    message_r.lpush('metrics', pickle.dumps(data))
    return '200'

@app.route('/gometrics', methods=['POST'])
def get_gometrics():
    data = request.json
    print("GO Mterics: ", data)
    print("Length: " + str(request.content_length) + " IP: " + str(request.remote_addr))
    message_g.lpush('metrics', pickle.dumps(data))
    return '200'

@app.route('/config', methods=['GET'])
def get_config():
    data = {
        "ping_target": [
            "www.google.com",
            "www.youtube.com",
            "www.whatsapp.com",
            "www.tiktok.com"
        ],
        "http_target": [
            "www.netflix.com",
            "www.youtube.com",
            "www.google.com",
            "www.tiktok.com"
        ],
        "speed_interval": 30
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


app.run(port=80, host='0.0.0.0')
