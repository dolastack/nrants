from django.contrib import admin
from .models import Feed, Article
from .forms import FeedForm
import feedparser
import datetime

def save_article(feedData, feed):
    for entry in feedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description
        article.publication_date = datetime.datetime(*(entry.published_parsed[0:6]))
        article.feed = feed
        article.save()

# Register your models here.

class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')

    def save_model(self, request, obj, form, change):
        if request.method == 'POST':
            form = FeedForm(request.POST)
            if form.is_valid():
                feed = form.save(commit=False)

            existingFeed = Feed.objects.filter(url=feed.url)
            if len(existingFeed)== 0:
                feedData = feedparser.parse(feed.url)
                if hasattr(feedData.feed, 'title' ):
                    feed.title = feedData.feed.title
                feed.save()
                save_article(feedData, feed)


admin.site.register(Feed, FeedAdmin)
admin.site.register(Article)