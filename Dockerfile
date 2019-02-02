FROM ubuntu:16.04
LABEL maintainer Soumyajit Dutta "sanudatta11@gmail.com"
RUN apt-get update -y && \
    apt-get install python-pip python-dev -y && \
    apt install libmysqlclient-dev -y

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "application.py" ]
EXPOSE 5000