from airflow import DAG
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

# Since all this does is take a day and convert then upload, there is no dependency
# between tasks or the past task runs. This is a go dog go type of dag
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "wait_for_downstream": False,
    "start_date": datetime(2016, 10, 2, 1, tzinfo=utc_tz),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "task_concurrency": 4,
    # "execution_timeout": timedelta(minutes=2)
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("hrrr_historical", default_args=default_args, schedule_interval=timedelta(days=1))

# Prepare commands that will execute a docker-compose call for the two tasks

# docker compose template on ssh_hrrr machince
# config file in docker image
docker_compose_file = '/home/ubuntu/config/docker-compose-hrrr.yml'
config_file = '/code/config/hrrr_historical.ini'

# convert_grib2nc command for conversion, this will use the execution date
hrrr = HRRR(docker_compose_file, config_file)
grib2nc = hrrr.get_compose_grib2nc(yesterday=True)

# upload to swift, use the execution date
swift = HRRR('/home/ubuntu/config/docker-compose-swift.yml', config_file)
upload_swift = swift.get_compose_upload_swift(log_file='/data/hrrr/logs/swift_historical.log', yesterday=True)

# delete the directory
delete_dir = hrrr.delete_hrrr_directory()

t1 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='convert_grib2nc',
    command=grib2nc,
    dag=dag)

t2 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='upload_swift',
    command=upload_swift,
    dag=dag)

t3 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='delete_empty_directory',
    command=delete_dir,
    dag=dag)

t1.set_downstream(t2)
t2.set_downstream(t3)
