from django.urls import path

from . import views

urlpatterns = [
    path('article/<int:id>', views.get_article, name="article"),
    path('article', views.post_article, name="post_article"),
    path("", views.redirect_docs),  # Redirect empty to the documentation
    path("test", views.test)
]
