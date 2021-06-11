import os
import json
import logging
from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration
from services.service_emblue import ServiceEmblue

app = Flask(__name__)
CORS(app)
app.debug = True

logger = logging.getLogger()

sentry_sdk.init(
    os.getenv('SENTRY_DNS'),
    integrations=[FlaskIntegration()],
    environment=os.getenv('env', 'dev')
)


@app.route("/emblue/public/v1/info")
def info():
    return Response('<html><h3>SERVICIO EMBLUE</h3></html>', status=200, headers={'Content-Type': 'text/html'})


@app.route("/emblue/public/v1/subscription", methods=['POST'])
@cross_origin()
def subscription():
    # print("input:", request.json)
    try:
        r = request.json
        data = ServiceEmblue().subscription(r)
        js = json.dumps(data)
        resp = Response(
            response=js,
            status=200,
            mimetype='application/json'
        )
        return resp
    except Exception as e:
        # capture_exception(e)
        return Response(
            response=json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/unsubscription", methods=['POST'])
@cross_origin()
def unsubscription():
    # print("input:", request.json)
    try:
        req = request.json
        r = ServiceEmblue().unsubscription(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/subscription_by_topic", methods=['POST'])
@cross_origin()
def subscription_by_topic():
    # print("input:", request.json)
    try:
        req = request.json
        r = ServiceEmblue().subscription_by_topic(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/unsubscription_by_topic", methods=['POST'])
@cross_origin()
def unsubscription_by_topic():
    # print("input:", request.json)
    try:
        req = request.json
        r = ServiceEmblue().unsubscription_by_topic(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/unsubscription_total", methods=['POST'])
def unsubscription_total():
    # print("input:", request.json)
    try:
        req = request.json
        r = ServiceEmblue().unsubscription_total(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/webhook", methods=['POST'])
def webhook():
    try:
        print(webhook.__name__)
        req = request.json  # POST
        # req = request.args  # GET
        print(req)
        return Response(json.dumps(req), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/bucket/file_list", methods=['POST'])
def bucket_file_list():
    try:
        print(bucket_file_list.__name__)
        req = request.json
        r = ServiceEmblue().bucket_file_list(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/bucket/file_get", methods=['POST'])
def bucket_file_get():
    try:
        print(bucket_file_get.__name__)
        req = request.json
        r = ServiceEmblue().bucket_file_get(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )


@app.route("/emblue/public/v1/test/method", methods=['POST'])
def test_method():
    try:
        print(test_method.__name__)
        req = request.json
        r = ServiceEmblue().test_method(req)
        return Response(json.dumps(r), status=200, mimetype='application/json')
    except Exception as e:
        # capture_exception(e)
        return Response(
            json.dumps({"status": False, "status_code": 500, "message": str(e)}),
            status=200,
            mimetype='application/json'
        )