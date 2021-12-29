import pathlib
import logging
import logging.handlers as lh
import contextlib

from gevent.pywsgi import WSGIServer
from . import create_app, db, models, conf


log = logging.getLogger(__package__)
log.setLevel("INFO")
logfile = pathlib.Path(conf["localeLogs"]).expanduser() / "server.log"
logfile.parent.mkdir(parents=True, exist_ok=True)
loghandler = lh.RotatingFileHandler(logfile, maxBytes=2*1024*1024, backupCount=5)
# Standard streams are unspecified here, thereby turning them off
logging.basicConfig(handlers=[loghandler])

app = create_app()
db.create_all(app=app)
http_server = WSGIServer(("0.0.0.0", 80), app, log=log)

with contextlib.suppress(KeyboardInterrupt):
    http_server.serve_forever()
