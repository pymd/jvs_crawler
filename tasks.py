from celery import Celery
import time
import os
import sys

from config import STATUS_NEW, STATUS_PROCESSING
from models import NavigationUrl, User, UserDetails
from uid_crawler import UidCrawler
from profile_crawler import ProfileCrawler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from jvs_crawler import DBSession

app = Celery('tasks', broker='amqp://localhost//')

# app.conf.task_routes = ([
#   ('save_urls_to_db', {'queue': 'urls'}),
#   ('save_usernames_to_db', {'queue': 'usernames'}),
#   ('save_profile_to_db', {'queue': 'profiles'}),
# ],)

app.conf.task_routes = {
    'jvs_crawler.tasks.save_urls_to_db': 'urls',
    'jvs_crawler.tasks.save_usernames_to_db': 'usernames',
    'jvs_crawler.tasks.save_profile_to_db': 'profiles',
}

# Contains all the celery tasks (functions to be called asynchronously)


@app.task
def taskname(arg):
    return arg


# db_conn = None

# @worker_process_init.connect
# def init_worker(**kwargs):
#     global db_conn
#     print('Initializing database connection for worker.')
#     db_conn = db.connect(DB_CONNECT_STRING)


# @worker_process_shutdown.connect
# def shutdown_worker(**kwargs):
#     global db_conn
#     if db_conn:
#         print('Closing database connectionn for worker.')
#         db_conn.close()


"""
@app.task
def save_url(url):
    row = search_db(url)
    if row:
        if row['status'] == STATUS_NEW:
            update_db(id=row['id'], status=STATUS_PROCESSING)
    else:
        # insert into db
        insert_db(url=url, hash=get_hash(url), status=STATUS_NEW)

    crawl_url.delay(url)
"""


@app.task
def save_urls_to_db(url_list):
    """
        - Check if URL already present in DB/save if not present
        - Call get_users
    """
    t0 = time.time()
    urls = list(set(url_list))
    n = len(urls)
    print('Writing %s urls to db' % str(n))

    for url in urls:
        try:
            # Check if already in db
            navigation_url = DBSession.query(NavigationUrl).filter(NavigationUrl.hash == hash(url))
            if (navigation_url is not None) and navigation_url.count() == 1:
                print('Found url: %s in DB' % str(url))
                url_id = navigation_url.first().id
            else:
                print('Url: %s not found in DB. Adding it ...' % str(url))
                navigation_url = NavigationUrl(url=url, hash=hash(url), status=STATUS_NEW)
                DBSession.add(navigation_url)
                DBSession.commit()
                url_id = navigation_url.id

            get_users.delay(url_id)

        except Exception as e:
            print('Exception while saving url: %s. Error: %s' % (url, str(e)))
            DBSession.rollback()
            raise e
    print(
        "SQLAlchemy ORM: Total time for " + str(n) +
        " urls " + str(time.time() - t0) + " secs")


@app.task
def get_users(url_id):
    """
        - Get URL from url_id
        - Update URL status to 'processing' in DB
        - Extract "usernames" from that page
        - Call save_user_name_to_db (Async)
        - Update URL status to 'done'       (WHEN ???)
    """
    if url_id is None:
        return
    print('Fetching users from url_id: ' + str(url_id))
    try:
        q = DBSession.query(NavigationUrl).filter(NavigationUrl.id == url_id)
        if q and q.count() == 1:

            # Get the url to fetch from and change its status in DB
            obj = q.first()
            url = obj.url
            print('Url object returned from DB is: ' + url)
            if obj.status == STATUS_NEW:
                q.update({'status': STATUS_PROCESSING})
                DBSession.commit()
            else:
                print('URL already processing/processed')
                return

            # Call get_usernames on that url
            print('Fetching usernames from URL: ' + str(url))
            usernames = UidCrawler.get_usernames(url=url)

            # Insert usernames to DB and update status of URL in DB
            # print('No of users:' + str(len(usernames)))
            print('Usernames: ' + str(list(usernames)))
            save_usernames_to_db.delay(usernames)

        else:
            DBSession.rollback()
            raise Exception('No such url_id: %s found in database' % str(url_id))
    except Exception as e:
        print(str(e))


@app.task
def save_usernames_to_db(usernames):
    """
        For all usernames:
            - Check if it exists in DB
            - Save it in DB
            - Call get_profile (Async)
    """
    t0 = time.time()
    usernames = list(set(usernames))
    n = len(usernames)
    print('Writing %s usernames to db' % str(n))

    for username in usernames:
        try:
            # Check if already in db
            user = DBSession.query(User).filter(User.username == username)
            if (user is not None) and user.count() == 1:
                print('Found user: %s in DB' % str(username))
                uid = user.first().id
            else:
                print('Username: %s not found in DB. Adding it ...' % str(username))
                user = User(username=username, status=STATUS_NEW)
                DBSession.add(user)
                DBSession.commit()
                uid = user.id

            get_profile.delay(uid)

        except Exception as e:
            print('Exception saving user: %s. Error: %s' % (username, str(e)))
            DBSession.rollback()
    print(
        "SQLAlchemy ORM: Total time for " + str(n) +
        " usernames " + str(time.time() - t0) + " secs")


@app.task
def get_profile(uid):
    """
        - Get username from uid
        - Update username status to 'processing' in DB
        - Extract "profile" for that username
        - Call save_profile_to_db (Async)
        - Update username status to 'done'      (WHEN ???)
    """
    if uid is None:
        print('Get_Profile called with uid: None')
        return
    print('Fetching profile for user with uid: ' + str(uid))
    try:
        q = DBSession.query(User).filter(User.id == uid)
        if q and q.count() == 1:

            # Get the username to fetch from and change its status in DB
            obj = q.first()
            username = obj.username
            print('User object returned from DB is: %s' % str(username))
            if obj.status == STATUS_NEW:
                q.update({'status': STATUS_PROCESSING})
                DBSession.commit()
            else:
                print('Username already processing/processed')
                return

            # Call get_user_details to get profile for that user
            print('Fetching profile for username: ' + str(username))
            user_details = ProfileCrawler(username=str(username)).get_user_details()

            # Insert user profile details to DB and update status of user in DB
            save_profile_to_db.delay(uid, user_details)

        else:
            DBSession.rollback()
            raise Exception('No such uid: %s found in database' % str(uid))
    except Exception as e:
        DBSession.rollback()
        print(str(e))


@app.task
def save_profile_to_db(uid, details):
    t0 = time.time()
    print('Saving profile for user: %s' % str(uid))

    try:
        user_details = DBSession.query(UserDetails).filter(UserDetails.uid == uid)
        if user_details is not None and user_details.count() == 1:
            print('Profile already exists in DB')
        else:
            name = details.get('UserName', None)
            gender = details.get('Gender', '')
            age = details.get('Age', '')
            religion = details.get('Religion', '')
            marital_status = details.get('Marital Status', '')
            occupation = details.get('Profession', '')
            education = details.get('Education', '')

            user_details = UserDetails(name=name, gender=gender, age=age,
                                       religion=religion, marital_status=marital_status,
                                       occupation=occupation, education=education, uid=uid)
            DBSession.add(user_details)
            DBSession.commit()
            # user_id = user_details.id
    except Exception as e:
        print('Exception saving user-profile details: %s. Error: %s' % (uid, str(e)))
        DBSession.rollback()

    print(
        "SQLAlchemy ORM: Total time for saving user details for uid: " + str(uid) +
        " = " + str(time.time() - t0) + " secs")
