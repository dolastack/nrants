from django.db import models
from django.utils import timezone
import hashlib
import datetime

# Create your models here.

class Feed(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField( max_length=200)
    
    

    class Meta:
        verbose_name = ("Feed")
        verbose_name_plural = ("Feeds")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class ArticlesManager(models.Manager):
    def articles_after(self, **kwargs):
        """get articles produced after a duration of time"""
        if kwargs is not None:
            for duration, value in kwargs.items():
                if duration == "minutes":
                    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=value)
                elif duration == "days":
                    time_delta = datetime.datetime.now() - datetime.timedelta(days=value)
                elif duration == "hours":
                    time_delta = datetime.datetime.now() - datetime.timedelta(hours=value)
                return self.filter(publication_date__gte = time_delta).order_by("-publication_date")

class Article(models.Model):
    feed = models.ForeignKey(Feed,  on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField( max_length=300)
    publication_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    article_id = models.CharField(max_length=200, primary_key=True)
    objects = ArticlesManager()

    def setID(self):
        idm = hashlib.sha1()
        temp = self.title + str(self.publication_date) + self.url
        idm.update(temp.encode())
        self.article_id = idm.hexdigest()

    class Meta:
        verbose_name = ("Article")
        verbose_name_plural = ("Articles")
        ordering = ("-publication_date",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Article_detail", kwargs={"pk": self.pk})
