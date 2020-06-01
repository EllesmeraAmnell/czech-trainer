import logging

from application import create_app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    logger.info('*' * 80)
    app.run(host='0.0.0.0', port=4000, passthrough_errors=True, debug=False)  # for public
    # app.run(port=4000, passthrough_errors=False)  # for debug
