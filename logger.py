import logging
import os

from datetime import datetime
from logging.handlers import RotatingFileHandler


def request_log(response):
    logger.info(f'Request URL: {response.url}')
    logger.info(f'Request Method: {response.request.method}')
    logger.info(f'Request Headers: {response.request.headers}')
    logger.info(f'Request Body: {response.request.body}')

    logger.info(f'Response Status Code: {response.status_code}')
    logger.info(f'Response Headers: {response.headers}')
    content_type = response.headers.get('Content-Type')

    if content_type and (content_type.startswith('image/') or content_type == 'application/octet-stream'):
        logger.info(f'Response Content: A picture')
    elif len(response.content) < 1000:
        logger.info(f'Response Content: {response.text}')
    else:
        logger.info(f'Response Content: 500 ERROR')


current_time = str(datetime.now()).replace(' ', '-').replace(':', '-').split('.')[0]
log_dir = 'logs/' + current_time

os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, 'app.log')

log_handler = RotatingFileHandler(log_filename, maxBytes=50 * 1024 * 1024, backupCount=3000)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[log_handler,
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)
