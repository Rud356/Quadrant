FROM python:3.7

ADD ./ /

RUN pip install -r requirements.txt

CMD ["python", "start.py"]
