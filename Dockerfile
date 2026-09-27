FROM python:3.12-slim

WORKDIR /app
COPY compare.py /app/compare.py
RUN mkdir -p /inputs /outputs

ENTRYPOINT ["python", "/app/compare.py"]
