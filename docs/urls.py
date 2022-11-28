from django.urls import path
from . import views

urlpatterns = [
  path("", views.index),  # Send blank to docs#1
  path("docs<int:n>", views.docs_n)  # Send others to docs#n
]
