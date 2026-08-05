FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .


COPY data/ingredients.json /app/data/ingredients.json

CMD ["sh", "-c", "python manage.py migrate --noinput && \
                  python manage.py collectstatic --noinput --clear && \
                  python manage.py load_ingredients && \
                  gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]