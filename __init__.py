import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from config import LOGGER_FORMAT, DB_CONNECTION_STRING
from models import Base

# Setup logging
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger('app')
logger.setLevel(10)     # debug

# Create tables if not present


db_url = DB_CONNECTION_STRING
engine = create_engine(db_url)
Base.metadata.bind = engine

logger.info('Creating mysql database if not present ...')
Base.metadata.create_all(engine)
logger.info('Done')

logger.info('Creating DBSession object')
DBSession = scoped_session(sessionmaker(bind=engine))
logger.info('Done')


# Check if celery is up and running
def get_celery_status():
    logger.info('Checking celery status ...')
    try:
        from celery.task.control import inspect
        stats = inspect().stats()
        if not stats:
            stats = {'ERROR': 'No running Celery workers were found.'}
            raise IOError('No celery worker found')
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        stats = {'ERROR': msg}
        logger.info(stats)
        raise(Exception(e))
    except ImportError as e:
        stats = {'ERROR': str(e)}
        logger.info(stats)
        raise Exception(e)
    return stats
