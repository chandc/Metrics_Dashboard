from flask import Flask, render_template, request
import logging
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask_opentracing import FlaskTracer
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory

from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)

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

tracer = init_tracer('frontend-trace')
metrics = PrometheusMetrics(app, group_by='endpoint')

@app.route('/')
def homepage():
    with tracer.start_span('main.html') as span:
        span.set_tag('message', 'Hello from main!')
        return render_template("main.html")


if __name__ == "__main__":
    app.run()