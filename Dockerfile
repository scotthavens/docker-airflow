FROM puckel/docker-airflow:1.10.3

# update the airflow config
ARG AIRFLOW_USER_HOME=/usr/local/airflow
COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

USER root

# This fixes permission issues on linux. 
# The airflow user should have the same UID as the user running docker on the host system.
# https://github.com/puckel/docker-airflow/issues/224

# Also, run docker images from docker-airflow
# https://stackoverflow.com/questions/43386003/airflow-inside-docker-running-a-docker-container
# ARG DOCKER_UID
RUN groupadd --gid 999 docker \
    && usermod -aG docker airflow

USER airflow

