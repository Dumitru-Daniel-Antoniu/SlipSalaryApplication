FROM python:3.10

EXPOSE 5000

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run"]