from flask import Flask, render_template, request

from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask_opentracing import FlaskTracer

app = Flask(__name__)


def initialize_tracer():
  config = Config(
      config={
          'sampler': {'type': 'const', 'param': 1}
      },
      service_name='frontend')
  return config.initialize_tracer() # also sets opentracing.tracer

flask_tracer = FlaskTracer(initialize_tracer, True, app)

@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()