from flask import Flask, jsonify
import redis
import pika
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = Flask(__name__)

# OpenTelemetry beállítás
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
FlaskInstrumentor().instrument_app(app)

cache = redis.Redis(host='redis', port=6379)

@app.route('/')
def home():
    latogatasok = cache.incr('szamlalo')
    return f"<h1>Mozi Jegyfoglaló</h1><p>Látogatások: {latogatasok}</p><p><a href='/jegyvetel'>Kattints ide egy jegy vásárlásához!</a></p>"

@app.route('/jegyvetel')
def jegyvetel():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='jegy_queue')
        channel.basic_publish(exchange='', routing_key='jegy_queue', body='Egy uj jegy eladva!')
        connection.close()
        return "<h3>Jegyvásárlás rögzítve!</h3><a href='/'>Vissza</a>"
    except Exception as e:
        return f"Hiba: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)