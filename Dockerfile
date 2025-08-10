FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cf_ddns_multi.py .

CMD ["python", "cf_ddns_multi.py"]
