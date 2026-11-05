FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask httpx streamlit

EXPOSE 5000

CMD ["python", "api.py"]