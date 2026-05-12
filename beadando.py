from flask import Flask, jsonify, render_template_string
import redis
import pika
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = Flask(__name__)

# --- OpenTelemetry (Jaeger) Beállítások ---
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
FlaskInstrumentor().instrument_app(app)

# --- Redis Kapcsolat ---
cache = redis.Redis(host='redis', port=6379)

# --- Modern HTML & CSS Design ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Mozi Jegyrendszer</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: #141414; 
            color: white; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            margin: 0; 
        }
        .card { 
            background: #1f1f1f; 
            padding: 2.5rem; 
            border-radius: 12px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.7); 
            text-align: center; 
            border-top: 6px solid #e50914; 
            max-width: 450px;
            width: 90%;
        }
        h1 { color: #e50914; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 2px; }
        .poster { 
            width: 100%; 
            height: 250px; 
            background-image: url('https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=500'); 
            background-size: cover; 
            background-position: center; 
            border-radius: 6px; 
            margin-bottom: 1.5rem; 
            box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
        }
        .counter { font-size: 1.1rem; color: #cccccc; margin-bottom: 2rem; background: #2b2b2b; padding: 10px; border-radius: 5px; }
        .counter strong { color: #e50914; font-size: 1.3rem; }
        .btn { 
            background-color: #e50914; 
            color: white; 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 1.1rem;
            transition: all 0.3s ease; 
            display: inline-block;
            cursor: pointer;
        }
        .btn:hover { background-color: #f40612; transform: translateY(-3px); box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4); }
        .status { margin-top: 2rem; padding: 15px; border-radius: 4px; background: rgba(76, 175, 80, 0.1); color: #4CAF50; font-weight: bold; line-height: 1.4; }
        .back-link { display: block; margin-top: 1.5rem; color: #808080; text-decoration: none; font-size: 0.9rem; }
        .back-link:hover { color: #ffffff; }
    </style>
</head>
<body>
    <div class="card">
        <div class="poster"></div>
        <h1>Mozi Jegyrendszer</h1>
        <div class="counter">Összes látogató a mai napon: <strong>{{ latogatasok }}</strong></div>
        
        {% if not msg %}
            <p>Válassza ki a legújabb premier filmünket!</p>
            <br>
            <a href="/jegyvetel" class="btn">🎫 JEGY VÁSÁRLÁSA</a>
        {% else %}
            <div class="status">{{ msg }}</div>
            <a href="/" class="back-link">← Vissza a kezdőlapra</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Redis számláló növelése
    latogatasok = cache.incr('szamlalo')
    return render_template_string(HTML_TEMPLATE, latogatasok=latogatasok)

@app.route('/jegyvetel')
def jegyvetel():
    try:
        # Üzenet küldése a RabbitMQ-nak
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='jegy_queue')
        channel.basic_publish(exchange='', routing_key='jegy_queue', body='Egy uj jegy eladva!')
        connection.close()
        
        # Jelenlegi látogatásszám lekérése a Redisből
        latogatasok = cache.get('szamlalo').decode()
        
        # Felhasználóbarát üzenet
        siker_msg = "🍿 Sikeres vásárlás! Jó szórakozást a filmhez! Az elektronikus jegyet továbbítottuk a rendszerünkbe."
        return render_template_string(HTML_TEMPLATE, latogatasok=latogatasok, msg=siker_msg)
    
    except Exception as e:
        return f"Hiba történt a rendszerben: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)