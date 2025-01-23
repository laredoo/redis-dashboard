FROM python:3.11-slim

WORKDIR /app

COPY runtime.py /app/runtime.py

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y unzip && apt-get clean

ENTRYPOINT ["python", "runtime.py"]
