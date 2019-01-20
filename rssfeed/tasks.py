from celery import task 
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
import feedparser
import facebook
from .models import  Article, Feed
from .admin import save_article


redis = redis.StrictRedis(host='localhost', port=6379, db=9)

cfg = {
   "page_id"      : "216809822168608",  # Step 1
   "access_token" : "EAAL3F6fnlNkBAFSHfhu9FEhZAuVtOSzvQXy2UiWw3Vnx16xFhrIOCyOLnFaB1wa31dND46mCi1ML8e8tObTkmaJMrZBpg4H4EuXZBHWynqDoBRSv51UxfWIaaFiFdTiYZCqpYwR1wM0ZBaJSjaLWlKjtoWScEAtHBiFTNJlFu54B8GHZBEwn8XNZAF5x5DSBoYZD"
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
    #attachment = {"name":article.title ,  "link" :article.url , "description": article.description}
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
