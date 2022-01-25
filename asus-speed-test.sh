#!/bin/sh
SCRIPT_DIR=.
LOG_DIR=./log
DATE=$(date '+%Y-%m-%d')

cd $SCRIPT_DIR

python3 asus_speedtest.py >>$LOG_DIR/asus-speedtest-$DATE-info.log 2>>$LOG_DIR/asus-speedtest-$DATE-error.log

