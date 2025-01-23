FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY runtime.py /app/

RUN mkdir -p /opt

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV REDIS_HOST=192.168.121.187
ENV REDIS_PORT=6379
ENV REDIS_INPUT_KEY=metrics
ENV REDIS_OUTPUT_KEY=lucaslaredo-proj3-output
ENV MONITORING_PERIOD=5
ENV FUNCTION_PATH=/opt/usermodule.py
ENV FUNCTION_ZIP=/opt/usermodule.zip
ENV FUNCTION_HANDLER=handler

CMD ["python", "runtime.py"]