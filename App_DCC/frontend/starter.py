from flask import Flask, render_template, request

from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask_opentracing import FlaskTracer
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory

from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)

metrics = PrometheusMetrics(app)


config = Config(
      config={
          'sampler': 
          {'type': 'const', 
           'param': 1}, 
          'logging':True,
      },
      service_name='frontend-app'
      #,validate=True,
      #metrics_factory=PrometheusMetricsFactory(service_name_label='frontend')
     )
   # also sets opentracing.tracer

flask_tracer = FlaskTracer(config.initialize_tracer(), True, app)

@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()