# Docker file for ftp-file-puller
FROM python:3.7.2-slim

#Install Cron
RUN apt-get update; exit 0
RUN apt-get -y install cron


# Create new user with home dir:
RUN useradd --system -ms /bin/bash ftp
RUN echo ftp:ftp | chpasswd
WORKDIR /home/ftp


COPY . .
##RUN chmod +x crontab/start_app.sh

# Add crontab file in the cron directory
##ADD /crontab/crontab /etc/cron.d/hello-cron

# Give execution rights on the cron job
##RUN chmod 0644 /etc/cron.d/hello-cron

# Create the log file to be able to run tail
##RUN touch /var/log/cron.log

RUN pip install --upgrade pip
RUN pip install -r pip_requirements/requirements.txt

# Run the command on container startup
##CMD sleep 5 && tail -f /var/log/cron.log

# Create the log file to be able to run tail
#RUN touch /var/log/cron.log
CMD bash -c 'echo Starting cron && touch /var/log/cron.log && cron &'

#RUN groupadd crond-users && \
#    chgrp crond-users /var/run/crond.pid && \
#    usermod -a -G crond-users ftp

# Run the command on container startup
# CMD cron && tail -f /var/log/cron.log
