FROM python:3.14.6

RUN apt-get update && \
apt-get install -y \
	gdal-bin \
	libgdal-dev \
	&& \
rm -rf /var/lib/apt/lists/*


WORKDIR webapp/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE "8080"

CMD ["gunicorn", "RutaYa.wsgi:application","--bind","0.0.0.0:8080"]
