FROM python:3.7

ADD ./ ./app

RUN pip install -r requirements.txt

CMD ["python", "start.py"]

EXPOSE 8080

VOLUME "/chat_resources"

ENV debug false
ENV allow_reg ture
ENV upload_folder /chat_resources
ENV db_conn_string mongodb://admin:unsafe_shit@localhost:27017
WORKDIR /app/