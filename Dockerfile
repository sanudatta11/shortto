FROM ubuntu:18.04
LABEL maintainer Soumyajit Dutta "sanudatta11@gmail.com"
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install python3-mysqldb -y && \
    apt-get install libmysqlclient-dev -y && \
    apt-get install nginx -y && \
    apt-get install -y build-essential && \
    apt-get install -y wget

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements-prod.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

COPY nginx.conf /etc/nginx
#

#CMD ["python3", "application.py" ]
RUN chmod +x ./start.sh
CMD ["./start.sh"]
EXPOSE 80
# EXPOSE 5000