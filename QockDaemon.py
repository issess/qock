# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python qock.py start

# standard python libs
import logging
import time

# third party libs
import sys
from daemon import runner
from logging import handlers

from Qock import main_program


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/tmp/qock.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            # Main code goes here ...
            # Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
            logger.debug("Start Qock...main_program!")
            main_program()
            logger.debug("End Qock...!")


app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = handlers.RotatingFileHandler(
    "/var/log/qock/qock.log",
    maxBytes= (1024 * 1024 * 512), # 512MB
    backupCount=3
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

daemon_runner = runner.DaemonRunner(app)
# This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.daemon_context.working_directory = "/home/pi/qock"
daemon_runner.do_action()
