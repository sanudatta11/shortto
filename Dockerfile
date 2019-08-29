FROM ubuntu:16.04
LABEL maintainer Soumyajit Dutta "sanudatta11@gmail.com"
RUN apt-get update -y && \
    apt-get install python-pip python-dev -y && \
    apt install libmysqlclient-dev -y && \
    apt install nginx -y && \
    apt install -y build-essential

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements-prod.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY nginx.conf /etc/nginx

COPY . /app

# CMD ["python", "application.py" ]
RUN chmod +x ./start.sh
CMD ["./start.sh"]
EXPOSE 80
# EXPOSE 5000