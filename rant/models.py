from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Rant(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'),
                      ('published', 'Published'),
                     )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
      related_name='rant_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, 
                              choices=STATUS_CHOICES,
                               default='draft')

    class Meta:
        verbose_name = ("Rant")
        verbose_name_plural = ("Rants")
        ordering = ("-publish",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Rant_detail", kwargs={"pk": self.pk})
