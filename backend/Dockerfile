FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY data/ingredients.json /app/data/ingredients.json

CMD ["sh", "-c", "python manage.py migrate --noinput && \
                  python manage.py collectstatic --noinput --clear && \
                  gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]