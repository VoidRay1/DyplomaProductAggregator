# pull official base image
FROM python:3.10.0-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG PROJ_DIR=/django_proj

RUN mkdir -p ${PROJ_DIR}
COPY ./backend ${PROJ_DIR}

# set work directory
WORKDIR ${PROJ_DIR}

# install dependencies
RUN pip install -U pip \
    pip install -r requirements.txt

COPY ./compose/django/entry.sh /entry.sh
RUN chmod +x /entry.sh
ENTRYPOINT [ "/entry.sh" ]