from datetime import datetime

class HRRR():

    def __init__(self, compose_file, config_file):
        """
        """
        self.base_compose = 'docker-compose -f {} run --rm'
        self.compose_file = compose_file
        self.config_file = config_file


    def get_start_date(self, kwargs):
        """
        Get 'start_date' 
        """

        ex_date = pd.to_datetime(kwargs['execution_date'])
        midnight_date = pd.to_datetime(datetime.date(ex_date))
        start_date = midnight_date

        return start_date

    def get_compose_command(self):
        """
        Assemble docker compose call and return

        Sample command would be:
        > docker-compose run weather_forecast_retrieval run_hrrr_retrieval_dates 
            --start '7/9/2019 09:00' --end '7/9/2019 10:00' /code/config/hrrr.ini
        """

        action = self.base_compose.format(self.compose_file)

        action += ' weather_forecast_retrieval run_hrrr_retrieval_dates --start {{ prev_execution_date.isoformat() }} --end {{ execution_date.isoformat() }}'
        action += ' {}'.format(self.config_file)

        return action


    def get_compose_grib2nc(self, yesterday=False):
        """
        Assemble docker compose call and return

        Sample command would be:
        > docker-compose run weather_forecast_retrieval convert_grib2nc 
            --start '7/9/2019 09:00' /code/config/hrrr.ini
        """

        action = self.base_compose.format(self.compose_file)

        if yesterday:
            action += ' weather_forecast_retrieval convert_grib2nc --start {{ yesterday_ds }}'
        else:
            action += ' weather_forecast_retrieval convert_grib2nc --start {{ prev_execution_date.isoformat() }}'
        action += ' {}'.format(self.config_file)

        return action

    def get_compose_upload_swift(self, log_file=None, yesterday=False):
        """
        Assemble docker compose call and return
        """

        if yesterday:
            file_pattern = 'hrrr.{{ yesterday_ds_nodash }}/hrrr.*.grib2'
        else:
            file_pattern = 'hrrr.{{ ds_nodash }}/hrrr.*.grib2'
        local_path = '/data/hrrr/grib2' # within the container
        container = 'hrrr'
        if log_file is None:
            log_file = '/data/hrrr/logs/swift.log' # within the container

        action = self.base_compose.format(self.compose_file)

        action += ' maestro copy_file_to_swift -d -p {} -l {} {} {}'.format(file_pattern, log_file, local_path, container) 
        
        return action


    def delete_hrrr_directory(self):
        """
        After all the stuff is done, delete the hrrr.YYYYMMDD directory
        """

        return 'rmdir /data/hrrr/grib2/hrrr.{{ yesterday_ds_nodash }}'

