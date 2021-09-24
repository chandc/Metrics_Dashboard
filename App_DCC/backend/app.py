from flask import Flask, render_template, request, jsonify

import pymongo
from flask_pymongo import PyMongo

import logging
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask_opentracing import FlaskTracer
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app)


app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'
#app.config['MONGO_URI'] = 'localhost:27017'

def initialize_tracer():
  config = Config(
      config={
          'sampler': {'type': 'const', 'param': 1}
      },
      service_name='backend',
      validate=True,
      metrics_factory=PrometheusMetricsFactory(service_name_label='backend') )
  return config.initialize_tracer() # also sets opentracing.tracer

mongo = PyMongo(app)

flask_tracer = FlaskTracer(initialize_tracer, True, app)

@app.route('/')
def homepage():
    hw = "Hello World"
    return(hw)


@app.route('/api')
def my_api():
    answer = "something"
    return jsonify(repsonse=answer)

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == "__main__":
    app.run()
