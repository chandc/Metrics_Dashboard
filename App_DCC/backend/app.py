from flask import Flask, render_template, request, jsonify

import pymongo
from flask_pymongo import PyMongo
import opentracing

import logging
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask_opentracing import FlaskTracer
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'
#app.config['MONGO_URI'] = 'localhost:27017'

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('backend-trace')

mongo = PyMongo(app)

metrics = PrometheusMetrics(app,group_by='endpoint')


@app.route('/')
def homepage():
    with tracer.start_span('hello world') as span:
         hw = "Hello World"
         span.set_tag('message', hw)
         return(hw)


@app.route('/api')
def my_api():
    with tracer.start_span('api') as span:
        answer = "something"
        span.set_tag('message', answer)
    return jsonify(repsonse=answer)

@app.route('/star', methods=['POST'])
def add_star():
        with tracer.start_span('star') as span:
            star = mongo.db.stars
            name = request.json['name']
            distance = request.json['distance']
            star_id = star.insert({'name': name, 'distance': distance})
            new_star = star.find_one({'_id': star_id })
            output = {'name' : new_star['name'], 'distance' : new_star['distance']}
            span.set_tag('status', 'OK')
        return jsonify({'result' : output})

if __name__ == "__main__":
    app.run()
