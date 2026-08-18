FROM python:3.12-slim
WORKDIR /challenge
RUN pip install --no-cache-dir cryptography
COPY _shared /challenge/_shared
COPY app.py /challenge/app.py
EXPOSE 8080
ENTRYPOINT ["python", "/challenge/app.py"]
