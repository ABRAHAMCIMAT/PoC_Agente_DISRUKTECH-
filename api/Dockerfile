FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn
COPY app app
# La BD demo es sintetica y reproducible: se genera al construir la imagen.
RUN python -m app.seed --reset
ENV PORT=8000
# API_KEY debe inyectarse como variable de entorno/secret del hosting.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
