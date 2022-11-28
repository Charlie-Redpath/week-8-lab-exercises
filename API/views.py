import os
import json
import time

from server.settings import BASE_DIR
from django.shortcuts import redirect
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError


def test(request):
  return HttpResponse("Hello, world.")

def redirect_docs(request):
  return redirect("/docs")

def get_article(request, id: int):
  if request.method != 'GET':
    return HttpResponseBadRequest("This endpoint only accepts GET requests.")

  path = os.path.join(BASE_DIR, f"articles/{id}")
  try:
    with open(path) as f:
      article = json.loads(f.read())
  except FileNotFoundError:
    return HttpResponseBadRequest("File not found.")
  except json.JSONDecodeError:
    return HttpResponseServerError("Bad file format, please let us know.")

  else:
    try:
      title = article["title"]
      sub_heading = article["sub_heading"]
      content = article["content"]
      date_published = article["date_published"]
    except KeyError:
      return HttpResponseServerError("Bad file format, please let us know.")
    else:
      return HttpResponse(json.dumps({
        "id": id, "title": title, "sub_heading": sub_heading, "content": content, "date_published": date_published
      }))

def post_article(request):
  if request.method != 'POST':
    return HttpResponseBadRequest("This endpoint only accepts POST requests. See docs.")

  path = os.path.join(BASE_DIR, "articles/")
  id = 0
  while os.path.exists(f"{path}{id}"): id += 1 

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
  else:
    with open(f"{path}{id}", "w") as f:
      json.dump(article, f)

    return HttpResponse(f"Article #{id} made.")
