FROM python:3.11-slim

WORKDIR /app

COPY proxy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy/ .
COPY data/prompts/ /data/prompts/

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
