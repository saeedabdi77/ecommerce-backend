# Use the official Python runtime image
FROM python:3.13

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade packaging tools first
RUN python -m pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "atashin_gallery_backend.wsgi:application"]
