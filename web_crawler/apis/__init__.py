from flask import Blueprint

from flask_restplus import Api, Namespace

blueprint = Blueprint('Web Crawler Service', __name__)

api = Api(
    blueprint,
    default='crawler',
    title='Web Crawler Service API',
    description='Crawl a web page and return top 10 web pages visited',
    version='v1',
    doc='/doc/'
)

ns = Namespace('v1', description='Web Crawler APIs',
               path='/app/')

api.add_namespace(ns)

# needed to register APIs in swagger
from web_crawler.apis.v1 import routes
