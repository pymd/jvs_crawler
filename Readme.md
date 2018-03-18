### JeevanSaathi.com Crawler  
The repo contains code for a simple crawler for jeevansaathi.com.  

Have intentionally not used a crawling tool like **scrapy** just to write something from scratch.

### Dependencies  
* Python3
* RabbitMQ
* MySQL

### Installation
- Install the dependencies
- Clone the repo locally
- Create a virtualenv
- Run:
	pip3 install -r requirements.txt
- Start a celery worker on tasks.py:
	celery worker -A tasks
- Run the crawler using:
	python3 crawler.py
