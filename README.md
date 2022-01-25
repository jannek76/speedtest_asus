# Asus speedtest

This script is able to login to ASUS RT-AX86U Wireless Router and use firmware ookla speedtest from remote server using ssh connection. Script also includes the possibility to write data to Influx database e.g. for monitoring purposes. This version currently uses InfluxDB 2.0.4 version.

NOTE! This script is intended to be used as an example. Script comes without any warranty & support. You have to also enable SSH connection to your server.

Script has dependencies to quite a few Python3 packages which are described in [requirements.txt](requirements.txt).

Install python dependies:

```bash
    pip3 install -r requirements.txt
```

## Configurations

To configurations of ASUS router unit and InfluxDB are done in [settings.yml](settings.yml) or you can overdrive all or some of configurations by giving overdrive values in `settings-overdrive.yml` file.

Example:
You have following values in [settings.yml](settings.yml)

```yml
ROUTER: "router ip address" # Router IP address
USER: "your_username"       # Router username
PASSWORD: "your_password"   # Router password
LOG_LEVEL: "INFO"           # Logging level
```

and you will give
`settings-overdrive.yml`

```yml
ROUTER: "xxx.yyy.zzz.a"
USER: "my_name"
PASSWORD: "passwd"
LOG_LEVEL: "DEBUG"
```

So `asus_speedtest.py` will use overdrived values values in script

## Run script

```bash
python3 asus_speedtest.py
```

or

Run script and saves log files to given locations

```sh
SCRIPT_DIR=.
LOG_DIR=./log
```

```bash
./asus-speed-test.sh
```