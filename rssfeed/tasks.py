from celery import task 
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
import feedparser
import facebook
from .models import  Article, Feed
from .admin import save_article



cfg = {
   "page_id"      : "216809822168608",  # Step 1
   "access_token" : "EAAL3F6fnlNkBANuexR7lLFOcrTRalacmZAZBBH9wafWOAwJJZAW7WgustAJFavFZAUgRD6emcGNhsZBIJIz8g5xeZA6FCQh7HUCMIw7txPjgXGgV4uP7du41DnlRzYpIcst52sPOY1CYYLz5XBJsQmKkdz4dt7cMOsBy3OiZAXdo7hErgKKnz4jOYV2dkGplZCQZD"
}

def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    # Get page token to post as the page. You can skip
    # the following if you want to post as yourself.
    resp = graph.get_object('me/accounts')
    page_access_token = None
    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
    graph = facebook.GraphAPI(page_access_token)
    return graph

graph_api = get_api(cfg)
#@periodic_task(run_every=(crontab(minute="*/15")))
def post_to_facebook():
    """Post new articles to facebook"""
    try:
        status = graph_api.put_object("me", "feed", message="hello")
    except facebook.GraphAPIError as er:
        print("There is a problem ", str(er))


@periodic_task(run_every=(crontab(minute="*/7")))
def feed_update():
    """background task to get update from feed """
    FEED_LIST = Feed.objects.all()
    for feed in FEED_LIST:
        feedData = feedparser.parse(feed.url)
        try:
            feed.title = feedData.feed.title
        except AttributeError:
            feed.title = "No title"
        feed.save()
        save_article(feedData,feed)
