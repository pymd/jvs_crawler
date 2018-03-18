# File containing a list of constants to be used across the application
import logging

BASE_URL = 'https://www.jeevansathi.com'
CELERY_WORKER_COUNT = 5


LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


STATUS_NEW = 'new'
STATUS_PROCESSING = 'processing'
STATUS_DONE = 'done'
STATUS_ERROR = 'error'

DB_CONNECTION_STRING = 'mysql://root:apg@localhost/jvs'
