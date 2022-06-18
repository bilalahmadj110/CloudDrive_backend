import pathlib
import logging
import logging.handlers as lh
import contextlib
import sys

from gevent.pywsgi import WSGIServer
from . import create_app, db, models, conf
# argparse
from argparse import ArgumentParser

# load from args
arg = ArgumentParser()
# get passed args
arg.add_argument('-p', '--port', type=int, default=81)
arg.add_argument('-ip', '--ipaddress', type=str, default="0.0.0.0")
# print the port
port = arg.parse_args().port
ip = arg.parse_args().ipaddress

print ("Starting server on ip %s and port %s" % (ip, port))

log = logging.getLogger(__package__)
log.setLevel("INFO")
logfile = pathlib.Path(conf["localeLogs"]).expanduser() / "server.log"
logfile.parent.mkdir(parents=True, exist_ok=True)
loghandler = lh.RotatingFileHandler(logfile, maxBytes=2*1024*1024, backupCount=5)
# Standard streams are unspecified here, thereby turning them off
logging.basicConfig(handlers=[loghandler])

app = create_app()
db.create_all(app=app)
http_server = WSGIServer((ip, port), app, log=log)

with contextlib.suppress(KeyboardInterrupt):
    http_server.serve_forever()
