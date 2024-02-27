FROM registry.access.redhat.com/ubi8/python-311:latest

WORKDIR /app

COPY requirements.txt /app
COPY server.py /app
COPY routes /app/routes
COPY templates /app/templates

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV NAME AUTH_TOKEN

CMD ["python", "server.py"]