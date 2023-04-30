FROM python:3.7-alpine AS backend-kubeflow-wheel

RUN apk update && apk add --no-cache tzdata && apk add --no-cache python3 cmd:pip3
RUN apk update && apk add --no-cache python3-dev libpq-dev nginx
RUN pip install --no-cache django gunicorn psycopg2-binary

ADD pipeline_administration_django /app
WORKDIR /app

RUN apk update && apk add --no-cache sudo bash openrc openssh
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN mkdir -p /run/openrc && touch /run/openrc/softlevel && rc-update add sshd default
RUN sleep 5
RUN  service sshd stop -Z && service sshd start
RUN echo "root:T3tDUcWNMQT5S" | chpasswd

EXPOSE 3500
CMD ["gunicorn", "--bind", "0.0.0.0:3500", "--workers", "3", "pipeline_administration_django.wsgi"]