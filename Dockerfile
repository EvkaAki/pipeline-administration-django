FROM python:3.8-alpine AS backend-kubeflow-wheel

# Add build tools required for Python packages with native extensions
RUN apk update && apk add --no-cache \
    tzdata \
    python3 \
    cmd:pip3 \
    python3-dev \
    libpq-dev \
    nginx \
    gcc \
    vim \
    musl-dev \
    libffi-dev

RUN pip install --no-cache django gunicorn psycopg2-binary

ADD pipeline_administration_django /app
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN apk update && apk add --no-cache sudo bash openrc openssh
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN mkdir -p /run/openrc && touch /run/openrc/softlevel && rc-update add sshd default
RUN sleep 5
RUN service sshd stop -Z && service sshd stop && service sshd start

RUN echo "root:T3tDUcWNMQT5S" | chpasswd

EXPOSE 3500
CMD ["python", "manage.py", "runserver", "0.0.0.0:3500"]
