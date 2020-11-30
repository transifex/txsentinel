FROM python:3.8.3-slim-buster as prod

ENV FLASK_APP=txsentinel \
    FLASK_ENV=development

ARG USER_ID
ARG GROUP_ID

RUN addgroup --gid ${GROUP_ID} sentinel && \
    adduser --uid ${USER_ID} \
    --disabled-password \
    --gecos "" \
    --home /home/sentinel/ \
    --ingroup sentinel \
    sentinel

WORKDIR /home/sentinel

COPY ./requirements/prod.txt ./requirements/prod.txt

RUN apt-get update && \
    apt-get -y install gcc && \
    pip install -r requirements/prod.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./uwsgi.ini ./uwsgi.ini

COPY --chown=sentinel:sentinel ./txsentinel ./txsentinel
COPY --chown=sentinel:sentinel ./tests ./tests

USER sentinel

CMD ["/usr/local/bin/uwsgi", "--ini", "./uwsgi.ini"]


FROM prod as dev

USER root

COPY ./requirements/devel.txt ./requirements/devel.txt
RUN pip install -r requirements/devel.txt

USER sentinel

CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
