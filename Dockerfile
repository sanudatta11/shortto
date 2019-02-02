FROM ubuntu:16.04

MAINTANER Soumyajit Dutta "sanudatta11@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev && \
    apt install libmysqlclient-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "application.py" ]
