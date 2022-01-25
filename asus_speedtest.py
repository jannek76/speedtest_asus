#!/usr/bin/env python3
from pathlib import Path

import sys
import datetime
import logging
import json
import hiyapyco

from flatten_json import flatten
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from tenacity import retry, stop_after_delay, wait_fixed, stop_after_attempt
from functools import partial

from ssh_client import RemoteClient


# Load used configurations from `settings.yml` and overdrive values
# from `settings-overdrive.yml`
conf = hiyapyco.load('settings.yml', 'settings-overdrive.yml', failonmissingfiles=False)

time_now = datetime.datetime.utcnow()

# Settings
ROUTER = conf['ROUTER']                          # Router IP address
PORT = conf['PORT']                              # Router port (default 22)
USER = conf['USER']                              # Router username
SSH_KEY = conf['SSH_KEY']                        # Router password converts str to bytes
LOG_LEVEL = conf['LOG_LEVEL']                    # Logging level, (default: INFO)
TIME_BETWEEN_CALLS = conf['TIME_BETWEEN_CALLS']  # Time between sequential calls, (seconds)
RETRIES = conf['RETRIES']                        # how many time retry
RETRY_INTERVAL = conf['RETRY_INTERVAL']          # wait time between retry call seconds

USEINFLUX = conf['INFLUXDB']['USEINFLUX']        # Whether to use Influx DB or not, set True or False

# Setup Influx database details in case that is used
if USEINFLUX:
    ifurl = conf['INFLUXDB']['ifurl']
    iftoken = conf['INFLUXDB']['iftoken']
    iforg = conf['INFLUXDB']['iforg']
    ifbucket = conf['INFLUXDB']['ifbucket']

OOKLA_RESP_TYPE = conf['OOKLA']['response']
OOKLA_CONFIG = conf['OOKLA']['configuration']

# Define shorthand decorator for the used settings.
retry_on__error = partial(
    retry,
    stop=(stop_after_delay(10) | stop_after_attempt(RETRIES)),  # max. 10 seconds wait.
    wait=wait_fixed(RETRY_INTERVAL),  # wait 400ms
)()

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL),
                    format=FORMAT)
logger = logging.getLogger(__name__)


class InfluxDB:

    def __init__(self, url, token, org, write_options=SYNCHRONOUS):
        self.ifclient = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.ifclient.write_api(write_options=write_options)

    """
    Close client
    """
    def logout(self):
        self.write_api.__del__()
        self.ifclient.__del__()

    # Write to Influx
    #@retry_on__error
    def influxwrite(self, result, measurement):
        fields = flatten(json.loads(result))

        body = {
                "measurement": measurement,
                "time": time_now,
                "fields": fields
        }

        logging.info('write to Influx: {}'.format(body))
        ifpoint = Point.from_dict(body)
        self.write_api.write(bucket=ifbucket, record=ifpoint)


class ASUS_SPEEDTEST:

    def __init__(self):
        self.remote = RemoteClient(ROUTER, PORT,  USER, SSH_KEY)
        self.influxdb = InfluxDB(ifurl, iftoken, iforg) if USEINFLUX else None

        self.ookla_cmd = 'ookla -c {} -f {}'.format(OOKLA_CONFIG, OOKLA_RESP_TYPE)
        #self.ookla_cmd = 'sh test.sh'

    def run_speedtest(self):
        resp = self.remote.execute_command(self.ookla_cmd)
        self.remote.disconnect()
        if USEINFLUX:
            self.influxdb.influxwrite(resp[0], 'speedtest')


def main():
    """ main method """
    speedtest = ASUS_SPEEDTEST()
    speedtest.run_speedtest()


if __name__ == "__main__":
    sys.exit(main())
