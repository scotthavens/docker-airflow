from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
import pendulum

from datetime import datetime, timedelta
from utils.hrrr import HRRR

# Default args from https://airflow.apache.org/_api/airflow/models/index.html#airflow.models.BaseOperator
# depends_on_past (bool) – when set to true, task instances will run sequentially 
# while relying on the previous task’s schedule to succeed. The task instance for 
# the start_date is allowed to run.
# task_concurrency (int) – When set, a task will be able to limit the concurrent 
# runs across execution_dates

utc_tz = pendulum.timezone("UTC")

# NOTE: Starting on the 1 hour as this will pull all data from 00:00 to 01:00
# TODO: Need this to basically be sequential since there could be a race condition for file conversion/upload
default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "wait_for_downstream": True,
    "start_date": datetime(2019, 7, 16, 1, tzinfo=utc_tz),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "task_concurrency": 1,
    # "execution_timeout": timedelta(minutes=2)
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("hrrr_retrevial", default_args=default_args, schedule_interval=timedelta(hours=1))

# Prepare commands that will execute a docker-compose call for
# the three tasks

# docker compose template on ssh_hrrr machince
# config file in docker image
docker_compose_file = '/home/ubuntu/config/docker-compose-hrrr.yml'
config_file = '/code/config/hrrr_dates.ini'

# run_weather_forecast_retrieval to get data from NOAA
hrrr = HRRR(docker_compose_file, config_file)
command = hrrr.get_compose_command()

# convert_grib2nc command for conversion
grib2nc = hrrr.get_compose_grib2nc()

# upload to swift
swift = HRRR('/home/ubuntu/config/docker-compose-swift.yml', config_file)
upload_swift = swift.get_compose_upload_swift()

t1 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='run_hrrr_retrieval_dates',
    command=command,
    dag=dag)

t2 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='convert_grib2nc',
    command=grib2nc,
    dag=dag)

t3 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='upload_swift',
    command=upload_swift,
    dag=dag)

t1.set_downstream(t2)
t2.set_downstream(t3)