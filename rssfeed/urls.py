from django.urls import path, include
from .views import ArticleListView
urlpatterns = [
    path('', ArticleListView.as_view(), name='articles' ),
]
