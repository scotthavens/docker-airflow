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

# Aims to download the data at 10am Pacific
default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "wait_for_downstream": True,
    "start_date": datetime(2019, 9, 25, 17, tzinfo=utc_tz),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(hours=1),
    "task_concurrency": 1,
    # "execution_timeout": timedelta(minutes=2)
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("water_supply_scraper", default_args=default_args, schedule_interval=timedelta(days=1))

# Yes, that is a space at the end, do not remove
# https://cwiki.apache.org/confluence/display/AIRFLOW/Common+Pitfalls
command = 'docker-compose exec -T web flask wss '

t1 = SSHOperator(
    ssh_conn_id='ssh_wss',
    task_id='run_wss',
    command=command,
    dag=dag)