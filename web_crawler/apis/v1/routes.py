import atexit
import uuid

from apscheduler.schedulers.background import BackgroundScheduler
from flask import request
from flask_restplus import Resource
from web_crawler.apis.v1.app_settings import CRAWLER_REQUIRED_KEYS

from web_crawler.apis import ns
from web_crawler.apis.v1.schema import crawler_schema
from web_crawler.utils.crawl_website import crawl_page
from web_crawler.utils.payload_processing import (
    parse_payload, check_required_keys
)


@ns.route('/crawl')
class CrawlPage(Resource):
    """
    Crawl a web page
    """

    @ns.doc('crawl_page')
    @ns.expect(crawler_schema)
    @ns.marshal_with(crawler_schema, code=201)
    def post(self):
        data = self.api.payload
        unique_id = uuid.uuid1()

        payload = parse_payload(request)
        # Check required params
        check_required_keys(payload, CRAWLER_REQUIRED_KEYS)

        def start_background_job():
            scheduler = BackgroundScheduler()
            scheduler.start()
            print("Scheduler Start")
            # It will executes the list of processes/methods in background
            scheduler.add_job(
                func=crawl_page,
                args=[data['site'], unique_id]
            )

            atexit.register(lambda: scheduler.shutdown())

        start_background_job()
        data['unique_id'] = unique_id
        return data, 201
