"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# from airflow.contrib.hooks import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator


# Default args from https://airflow.apache.org/_api/airflow/models/index.html#airflow.models.BaseOperator
# depends_on_past (bool) – when set to true, task instances will run sequentially 
# while relying on the previous task’s schedule to succeed. The task instance for 
# the start_date is allowed to run.
# task_concurrency (int) – When set, a task will be able to limit the concurrent 
# runs across execution_dates

default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "start_date": datetime.now() - timedelta(minutes=20),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "task_concurrency": 1
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("ssh_test", default_args=default_args, schedule_interval=timedelta(seconds=10))

t1_bash = """
echo 'Hello World'
"""
t1 = SSHOperator(
    ssh_conn_id='ssh_hrrr',
    task_id='test_ssh_operator',
    command=t1_bash,
    dag=dag)
