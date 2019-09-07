from flask_restplus import fields

from web_crawler.apis import api

crawler_model = api.model('Crawler', {
    'site': fields.String(
        required=True,
        readOnly=True,
        description='The website you want to crawl',
        example='https://www.greatlearning.in/'
    )
})

crawler_schema = api.clone('Crawl New Website', crawler_model)
