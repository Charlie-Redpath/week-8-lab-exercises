"""API Endpoints"""

# Imports
import os
import json
import time

from server.settings import BASE_DIR
from django.shortcuts import redirect
from django.http import (HttpResponse, HttpResponseBadRequest, 
  HttpResponseServerError, HttpRequest)
from typing import Dict
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class User:
  """Simple User dataclass for logging"""
  failures: int
  last_post: float
  last_get: float

USERS: Dict[str, User] = defaultdict(lambda: User(0, time.time(), time.time()))


def test(request: HttpRequest):
  """Simple test endpoint"""
  return HttpResponse("Hello, world.")


def redirect_docs(request: HttpRequest):
  """Redirects to root of docs"""
  return redirect("/docs")


def get_article(request: HttpRequest, id: int):
  """Endpoint to get an article, with ID = id

    If article id exists, returns the JSON
  """

  # Only accepts GET
  if request.method != 'GET':
    return HttpResponseBadRequest("This endpoint only accepts GET requests.")

  # Try to access and load the file
  path = os.path.join(BASE_DIR, f"articles/{id}")
  try:
    with open(path) as f:
      article = json.loads(f.read())
  except FileNotFoundError:
    return HttpResponseBadRequest("File not found.")
  except json.JSONDecodeError:
    return HttpResponseServerError("Bad file format, please let us know.")

  # Got the file contents fine
  else:
    try:
      title = article["title"]
      sub_heading = article["sub_heading"]
      content = article["content"]
      date_published = article["date_published"]
    except KeyError:
      return HttpResponseServerError("Bad file format, please let us know.")
    
    # Got all content ok
    else:
      return HttpResponse(json.dumps({
        "id": id, "title": title, "sub_heading": sub_heading, "content": content, "date_published": date_published
      }))

def post_article(request: HttpRequest):
  """Endpoint to add an article
  
    Requires POST data in form:
      {
        "title": <title>,
        "sub_heading": <sub_heading>,
        "content": <content>
      }
    Other fields will be ignored

    On success, returns a message containing the new id
  """

  # Only accepts POST
  if request.method != 'POST':
    return HttpResponseBadRequest("This endpoint only accepts POST requests. See docs.")

  # Find next available file
  path = os.path.join(BASE_DIR, "articles/")
  id = 0
  while os.path.exists(f"{path}{id}"): id += 1 

  # Get data from request
  post_data = request.POST
  try:
    article = {
      "id": id,
      "title": post_data["title"],
      "sub_heading": post_data["sub_heading"],
      "content": post_data["content"],
      "date_published": time.strftime("%d/%m/%Y")
    }
  except KeyError:
    return HttpResponseBadRequest("Bad data format. See docs.")

  # Data was okay
  else:
    with open(f"{path}{id}", "w") as f:
      json.dump(article, f)

    return HttpResponse(f"Article #{id} made.")
