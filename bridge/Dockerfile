FROM python:3.14.6

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["python", "-m", "app.bridge"]
