import multiprocessing as mp
import os

from waitress import serve

from mindsdb.api.http.initialize import initialize_app
from mindsdb.integrations.libs.ml_exec_base import process_cache
from mindsdb.interfaces.database.integrations import integration_controller
from mindsdb.interfaces.storage import db
from mindsdb.utilities.config import Config
from mindsdb.utilities.functions import init_lexer_parsers
from mindsdb.utilities import log

logger = log.getLogger(__name__)


def start(verbose, no_studio, with_nlp):
    logger.info("HTTP API is starting..")
    config = Config()
    is_cloud = config.get("cloud", False)

    server = os.environ.get("MINDSDB_DEFAULT_SERVER", "waitress")
    db.init()
    init_lexer_parsers()
    app = initialize_app(config, no_studio, with_nlp)

    port = config["api"]["http"]["port"]
    host = config["api"]["http"]["host"]

    process_cache.init(
        {
            integration_controller.handler_modules["lightwood"].Handler: 4
            if is_cloud
            else 1
        }
    )
    logger.info("Done doing cache stuff..")

    if server.lower() == "waitress":
        logger.debug("Serving HTTP app with waitress..")
        serve(
            app,
            host="*" if host in ("", "0.0.0.0") else host,
            port=port,
            threads=16,
            max_request_body_size=1073741824 * 10,
            inbuf_overflow=1073741824 * 10,
        )
    elif server.lower() == "flask":
        logger.debug("Serving HTTP app with flask..")
        # that will 'disable access' log in console
        # logger = log.getLogger("werkzeug")

        app.run(
            debug=False,
            port=port,
            host=host,
            use_reloader=True,
            use_debugger=True,
            passthrough_errors=True,
        )
    elif server.lower() == "gunicorn":
        logger.debug("Serving HTTP app with gunicorn..")
        try:
            from mindsdb.api.http.gunicorn_wrapper import StandaloneApplication
        except ImportError:
            logger.error(
                "Gunicorn server is not available by default. If you wish to use it, please install 'gunicorn'"
            )
            return

        def post_fork(arbiter, worker):
            db.engine.dispose()

        options = {
            "bind": f"{host}:{port}",
            "workers": mp.cpu_count(),
            "timeout": 600,
            "reuse_port": True,
            "preload_app": True,
            "post_fork": post_fork,
            "threads": 4,
        }
        StandaloneApplication(app, options).run()
