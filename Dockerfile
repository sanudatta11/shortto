FROM ubuntu:18.04
LABEL maintainer Soumyajit Dutta "sanudatta11@gmail.com"
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt install libmysqlclient-dev -y && \
    apt install nginx -y && \
    apt install -y build-essential

RUN echo "deb https://repo.logdna.com stable main" | sudo tee /etc/apt/sources.list.d/logdna.list
RUN wget -O- https://repo.logdna.com/logdna.gpg | sudo apt-key add -
RUN apt-get update
RUN apt-get install logdna-agent < "/dev/null" # this line needed for copy/paste
RUN logdna-agent -k b323e705204ab084acd3844a648ae13b # this is your unique Ingestion Key
# /var/log is monitored/added by default (recursively), optionally add more dirs with:
# sudo logdna-agent -d /path/to/log/folders
# You can configure the agent to tag your hosts with:
# sudo logdna-agent -t mytag,myothertag
RUN update-rc.d logdna-agent defaults
RUN /etc/init.d/logdna-agent start

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements-prod.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

#COPY nginx.conf /etc/nginx
#

CMD ["python3", "application.py" ]
#RUN chmod +x ./start.sh
#CMD ["./start.sh"]
EXPOSE 80
# EXPOSE 5000