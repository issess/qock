#!/bin/bash
# Copyright (c) 2017 issess
# All rights reserved.
#
# Author: Bob Bobson, 2012
#
# Please send feedback to bob@bob.com
#
# /etc/init.d/Qock
#
### BEGIN INIT INFO
# Provides: Qock
# Required-Start:
# Should-Start:
# Required-Stop:
# Should-Stop:
# Default-Start: 3 5
# Default-Stop: 0 1 2 6
# Short-Description: qock daemon process
# Description: Runs up the qock daemon process
### END INIT INFO

# Activate the python virtual environment
#. /path_to_virtualenv/activate

cd /home/pi/qock_dev/

case "$1" in
    start)
        echo "Starting qock server"
        # Start the daemon
        python QockDaemon.py start
        ;;
    stop)
        echo "Stopping qock server"
        # Stop the daemon
        python QockDaemon.py stop
        ;;
    restart)
        echo "Restarting qock server"
        python QockDaemon.py restart
        ;;
    *)
        # Refuse to do other stuff
        echo "Usage: /etc/init.d/qock {start|stop|restart}"
        exit 1
        ;;
esac

exit 0