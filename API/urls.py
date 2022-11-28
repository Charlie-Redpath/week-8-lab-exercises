from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('article/<int:id>', views.get_article, name="article"),
    path('article', views.post_article, name="post_article"),
]
