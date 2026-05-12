from flask import Flask, render_template_string, request
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

# --- HTML Sablon (A pontosan kért XenomaX design) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>XenomaX Mozi | Premium Booking</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Lato', sans-serif; 
            background-color: #0b0b0b; 
            color: #ffffff; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0; 
        }
        .card { 
            background: #141414;
            padding: 2.5rem; 
            border-radius: 20px; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.9); 
            max-width: 600px;
            width: 90%;
            border-top: 5px solid #e50914; 
            text-align: center; 
        }
        
        /* HERO SZEKCIÓ: SZÉKSOR ÉS NEON X */
        .hero-banner {
            width: 100%;
            height: 220px;
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                        url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1000&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: inset 0 0 50px #000;
        }
        .neon-x {
            font-family: 'Bebas Neue', cursive;
            font-size: 100px;
            color: #e50914;
            text-shadow: 0 0 10px #e50914, 0 0 30px #e50914, 0 0 60px #e50914;
            user-select: none;
        }

        h1 { 
            font-family: 'Bebas Neue', cursive; 
            color: #e50914; 
            font-size: 3.5rem; 
            margin: 0; 
            letter-spacing: 6px; 
        }
        .tagline { font-size: 0.8rem; color: #555; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 25px; }
        
        .section { background: #1c1c1c; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: left; border: 1px solid #2a2a2a; }
        .section h3 { margin: 0 0 20px 0; font-size: 0.9rem; color: #e50914; text-transform: uppercase; letter-spacing: 2px; }
        
        /* FILMVÁLASZTÓ RÁCS PLAKÁTOKKAL */
        .movie-grid { display: flex; gap: 15px; justify-content: space-between; }
        .movie-card { flex: 1; cursor: pointer; text-align: center; }
        .movie-card img { 
            width: 100%; 
            height: 220px; 
            object-fit: cover; 
            border-radius: 8px; 
            border: 3px solid transparent; 
            transition: all 0.3s ease; 
        }
        .movie-card p { font-size: 0.7rem; margin-top: 10px; color: #888; font-weight: bold; text-transform: uppercase; }
        
        input[type="radio"] { display: none; }
        input[type="radio"]:checked + label img { 
            border-color: #e50914; 
            transform: scale(1.05); 
            box-shadow: 0 0 20px rgba(229, 9, 20, 0.6); 
        }
        
        select { width: 100%; padding: 12px; border-radius: 6px; background: #2b2b2b; color: white; border: 1px solid #444; font-size: 1rem; cursor: pointer; outline: none; }
        
        .btn { background: #e50914; color: white; border: none; padding: 18px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 1.2rem; cursor: pointer; transition: 0.3s; font-family: 'Bebas Neue'; letter-spacing: 2px; }
        .btn:hover { background: #ff0a16; transform: translateY(-3px); box-shadow: 0 10px 25px rgba(229, 9, 20, 0.5); }
        
        /* SIKERES FOGLALÁS DOBOZ */
        .success-box { background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; padding: 25px; border-radius: 12px; color: #4CAF50; }
        .success-box h2 { font-family: 'Bebas Neue'; font-size: 2.5rem; margin-top: 0; }
    </style>
</head>
<body>
    <div class="card">
        <div class="hero-banner">
            <div class="neon-x">X</div>
        </div>
        
        <h1>XENOMAX</h1>
        <div class="tagline">The Ultimate Cinema Experience</div>
        
        {% if not msg %}
        <form action="/jegyvetel" method="get">
            <div class="section">
                <h3>1. Válasszon filmet:</h3>
                <div class="movie-grid">
                    <div class="movie-card">
                        <input type="radio" name="film" id="m1" value="Dűne: Második rész" checked>
                        <label for="m1">
                            <img src="https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzQyXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg" alt="Dune 2">
                            <p>Dűne 2.</p>
                        </label>
                    </div>
                    <div class="movie-card">
                        <input type="radio" name="film" id="m2" value="Oppenheimer">
                        <label for="m2">
                            <img src="https://m.media-amazon.com/images/M/MV5BMDBmYTZjNjctNDRhNS00YzdkLWIwZTMtN2VmOTcxMDExZDFmXkEyXkFqcGdeQXVyNDUyOTg3Njg@._V1_FMjpg_UX1000_.jpg" alt="Oppenheimer">
                            <p>Oppenheimer</p>
                        </label>
                    </div>
                    <div class="movie-card">
                        <input type="radio" name="film" id="m3" value="Szegény Párák">
                        <label for="m3">
                            <img src="https://m.media-amazon.com/images/M/MV5BNGIyYWMzNjUtYmZmYy00ZmE1LWJlODMtMTU0MzQ0YjI5ZGRjXkEyXkFqcGdeQXVyMTE0MzY0NjE1._V1_FMjpg_UX1000_.jpg" alt="Poor Things">
                            <p>Szegény Párák</p>
                        </label>
                    </div>
                </div>
            </div>

            <div class="section">
                <h3>2. Válasszon időpontot:</h3>
                <select name="idopont">
                    <option>Ma - 18:30 (PREMIUM)</option>
                    <option>Ma - 21:00 (VIP)</option>
                    <option>Holnap - 17:45 (IMAX)</option>
                </select>
            </div>

            <button type="submit" class="btn">🎫 JEGY FOGLALÁSA</button>
        </form>
        <p style="color: #333; font-size: 0.8rem; margin-top: 15px;">Verified Visitors: {{ latogatasok }}</p>
        
        {% else %}
        <div class="success-box">
            <h2>✨ SIKERES FOGLALÁS!</h2>
            <p style="font-size: 1.1rem;"><strong>Film:</strong> {{ film }}</p>
            <p style="font-size: 1.1rem;"><strong>Időpont:</strong> {{ idopont }}</p>
            <hr style="border: 0; border-top: 1px solid rgba(76, 175, 80, 0.3); margin: 15px 0;">
            <p style="font-size: 0.9rem; opacity: 0.8;">Köszönjük, hogy a XenomaX-ot választotta!</p>
        </div>
        <a href="/" style="display:block; margin-top:20px; color:#888; text-decoration:none;">← Vissza a filmekhez</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    latogatasok = cache.incr('szamlalo')
    return render_template_string(HTML_TEMPLATE, latogatasok=latogatasok)

@app.route('/jegyvetel')
def jegyvetel():
    try:
        film = request.args.get('film', 'XenomaX Premier')
        idopont = request.args.get('idopont', 'Standard Time')
        
        # RabbitMQ küldés
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='jegy_queue')
        channel.basic_publish(exchange='', routing_key='jegy_queue', body=f'XENOMAX BOOKING: {film} | {idopont}')
        connection.close()
        
        latogatasok = cache.get('szamlalo').decode()
        return render_template_string(HTML_TEMPLATE, latogatasok=latogatasok, msg=True, film=film, idopont=idopont)
    except Exception as e:
        return f"System Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)