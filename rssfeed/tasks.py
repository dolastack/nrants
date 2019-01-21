from celery import task 
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
from django.db.models.signals import post_save
import feedparser
import facebook
import redis
from .models import  Article, Feed
from .admin import save_article


redis = redis.StrictRedis(host='localhost', port=6379, db=9)

cfg = {
   "page_id"      : "216809822168608",  # Step 1
   "access_token" : "EAAL3F6fnlNkBAASwO3R8MbqlfKdSJZCCnZBN3Qfj6JtKGoowiDyM3jfr4QuUY76wa1TvNsW6jkZAfqlgQ8JSo09GkUZBllYI0TE76bG21hoDpZB929ZBPdyRzmwvoAfh0KzdxcZCZBk1ZADQK4fqocIVxSKkAijWWTTkZD"
}

#periodically get new articles
def get_latest_article(sender,  **kwargs):
    #videos = YoutubeVideo.objects.videos_after(minutes=12)
    if kwargs['created']:
        article = kwargs['instance']
        redis.lpush('articles', article.article_id )

#post save signal connect
post_save.connect(get_latest_article, sender=Article)

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
@periodic_task(run_every=(crontab(minute="*/15")))
def post_to_facebook():
    for i in range(2):
        if redis.llen('articles') > 0:
            article = Article.objects.get(article_id = redis.lpop('articles').decode())

            """Post new articles to facebook"""
            try:
                status = graph_api.put_object("me", "feed", message=article.title, link=article.url)
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
