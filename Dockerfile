# Docker file for ftp-file-puller
FROM python:3.7.2-slim
                                       
COPY pip_requirements/requirements.txt /root/pip_requirements/

# Install pip requirements, and add the crontab file as a cronjob
RUN pip install --upgrade pip; pip install -r /root/pip_requirements/requirements.txt;

COPY . /root

# Run cron on startup
ENTRYPOINT ["python", "/root/ftp-files-puller.py"]
