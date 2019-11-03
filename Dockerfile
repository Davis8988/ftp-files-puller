# Docker file for ftp-file-puller
FROM python:3.7.2-slim


# Add crontab file in the cron directory
ADD /crontab/ftp-puller-crontab /etc/cron.d/ftp-puller/

# Give execution rights on the cron job 
# & Create the log file to be able to run tail 
RUN chmod 0644 /etc/cron.d/ftp-puller; \
    touch /var/log/cron.log; \
    touch /root/.cronenv ; \
    chmod 0700 /root/.cronenv
    

# Update apt-get & install utilities
RUN apt-get update; apt-get -y install cron \
                                       vim 
                                       
# Allow logging for cron using rsyslog:
# RUN sed -i 's|^#cron.[*].*|cron.*                          /var/log/cron.log|' /etc/rsyslog.conf


COPY . /root

# Install pip requirements, and add the crontab file as a cronjob
RUN pip install --upgrade pip; pip install -r /root/pip_requirements/requirements.txt; \
    crontab /etc/cron.d/ftp-puller/ftp-puller-crontab


# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
