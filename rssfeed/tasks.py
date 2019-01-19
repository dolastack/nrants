from celery import task 
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
import feedparser
from .models import  Article, Feed


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
