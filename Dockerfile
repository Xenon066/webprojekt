# 1. Letöltünk egy alap Pythont a konténerbe
FROM python:3.10-slim

# 2. Létrehozunk egy munkamappát a konténeren belül
WORKDIR /app

# 3. Bemásoljuk a fájljainkat (beadando.py, requirements.txt) a konténerbe
COPY . /app

# 4. Feltelepítjük a bevásárlólistán (requirements.txt) szereplő dolgokat
RUN pip install -r requirements.txt

# 5. Kinyitjuk az 5000-es ajtót (portot)
EXPOSE 5000

# 6. Megmondjuk, mi legyen a parancs, amikor elindul a konténer
CMD ["python", "beadando.py"]
