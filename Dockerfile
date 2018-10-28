FROM python:3

COPY app.py /app/app.py
COPY mediasync /app/mediasync

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app
CMD python app.py