FROM python:3.12-slim

WORKDIR /app

ENV REDIS_HOST=192.168.121.187
ENV REDIS_PORT=6379
ENV REDIS_INPUT_KEY=lucaslaredo-proj3-output

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 55455

CMD ["streamlit", "run", "app.py", "--server.port=55455", "--server.address=0.0.0.0"]