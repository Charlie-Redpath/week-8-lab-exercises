"""API Endpoints"""

# Imports
import os
import json
import time
import random

from server.settings import BASE_DIR
from django.shortcuts import redirect
from django.http import (HttpResponse, HttpResponseBadRequest,
  HttpResponseServerError, HttpRequest, HttpResponseRedirect)
from typing import Dict
from dataclasses import dataclass
from collections import defaultdict

# Profanity filter
from .profanity import profanity_filter
FILTER = profanity_filter.ProfanityFilter()


@dataclass
class User:
  """Simple User dataclass for logging"""
  failures: int
  # Timeout warnings
  warnings: float
  # Last post/get *include* fails
  last_req: float = 0
  # When the last block started
  blocked_at: float = 0

USERS: Dict[str, User] = defaultdict(lambda: User(0, 0))
MIN_SEP = .1  # Requests must be .01 seconds apart
MAX_FAIL = 10  # Maximum failures before timeout
MAX_WARN = 3  # Number of MIN_SEP violations
FAIL_TIMEOUT = 60  # Timeout in seconds after MAX_FAIL hit


def get_client_ip(request: HttpRequest) -> str:
  """Returns the client IP from a request
    Source: https://stackoverflow.com/a/4581997
  """
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip


def fail(ip: str):
  """Registers a request fail from IP"""
  USERS[ip].failures += 1


def allowed(u: User, prev_req: float) -> int:
  """Determines whether to allow the request, based on the user
    prev_req: the time of the request *before* this one

    Return:
      0: allowed
      1: timeout from fails
      2: timeout from frequency
  """
  t = time.time()

  if u.failures >= MAX_FAIL:
    u.blocked_at = t
    u.failures = 0
    return 1

  if u.warnings >= MAX_WARN:
    u.blocked_at = t
    u.warnings = 0
    return 2

  if t - u.blocked_at < FAIL_TIMEOUT:
    return 1

  if t - prev_req < MIN_SEP:
    u.warnings += 1
    return 0

  return 0

def test(request: HttpRequest):
  """Simple test endpoint"""
  return HttpResponse("Hello, world.")


def redirect_docs(request: HttpRequest):
  """Redirects to root of docs"""
  return redirect("/docs")


def get_article(request: HttpRequest, id: int, bypass_limits=False):
  """Endpoint to get an article, with ID = id

    If article id exists, returns the JSON
  """

  ip = get_client_ip(request)
  prev = USERS[ip].last_req
  USERS[ip].last_req = time.time()

  # Check allowed
  if not bypass_limits:
    match allowed(USERS[ip], prev):
      case 1:
        return HttpResponseBadRequest(
          f"Too many failed requests, try again in {FAIL_TIMEOUT}s."
        )
      case 2:
        resp = HttpResponse(f"You have been rate limited; limit requests to {MIN_SEP}/s")
        resp.status_code = 429
        return resp

  # Only accepts GET
  if request.method != 'GET':
    fail(ip)
    return HttpResponseBadRequest("This endpoint only accepts GET requests.")

  # Try to access and load the file
  path = os.path.join(BASE_DIR, f"articles/{id}")
  try:
    with open(path) as f:
      article = json.loads(f.read())
  except FileNotFoundError:
    fail(ip)
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
      # Don't fail this as is a sever error
      return HttpResponseServerError("Bad file format, please let us know.")

    # Got all content ok
    else:
      return HttpResponse(json.dumps({
        "id": id, "title": title, "sub_heading": sub_heading, "content": content, "date_published": date_published
      }))


def post_article(request: HttpRequest, bypass_limits=False):
  """Endpoint to add an article

    Requires POST data in form:
      {
        "title": <title>,
        "sub_heading": <sub_heading>,
        "content": <content>
      }
    Other fields will be ignored

    On success, redirects to the new article with the deletion key as a parameter
  """

  ip = get_client_ip(request)
  prev = USERS[ip].last_req
  USERS[ip].last_req = time.time()

  # Check allowed
  if not bypass_limits:
    match allowed(USERS[ip], prev):
      case 1:
        return HttpResponseBadRequest(
          f"Too many failed requests, try again in {FAIL_TIMEOUT}s."
        )
      case 2:
        resp = HttpResponse(f"You have been rate limited; limit requests to {MIN_SEP}/s")
        resp.status_code = 429
        return resp

  # Only accepts POST
  if request.method != 'POST':
    fail(ip)
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
    fail(ip)
    return HttpResponseBadRequest("Bad data format. See docs.")

  # Clean profanity
  for key in ("title", "sub_heading", "content"):
    article[key] = FILTER.censor(article[key])

  key = "".join([chr(ord("a") + random.randint(0, 25)) for _ in range(10)])
  article["key"] = hash(key)

  # Data was okay
  with open(f"{path}{id}", "w") as f:
    json.dump(article, f)

  return HttpResponseRedirect(f"/API/article/{id}?key={key}")


def delete_article(request: HttpRequest, id: int, bypass_limits=False):
  """Endpoint to delete an article, given the key:

    POST data:
      {
        "key": <key>
      }
  """

  ip = get_client_ip(request)
  prev = USERS[ip].last_req
  USERS[ip].last_req = time.time()

  # Check allowed
  if not bypass_limits:
    match allowed(USERS[ip], prev):
      case 1:
        return HttpResponseBadRequest(
          f"Too many failed requests, try again in {FAIL_TIMEOUT}s."
        )
      case 2:
        resp = HttpResponse(f"You have been rate limited; limit requests to {MIN_SEP}/s")
        resp.status_code = 429
        return resp

  # Only accepts POST
  if request.method != 'POST':
    fail(ip)
    return HttpResponseBadRequest("This endpoint only accepts POST requests. See docs.")

  # Get key from article and request
  path = os.path.join(BASE_DIR, f"articles/{id}")
  try:
    with open(path) as f:
      article = json.loads(f.read())
  except FileNotFoundError:
    fail(ip)
    return HttpResponseBadRequest("File not found.")
  except json.JSONDecodeError:
    return HttpResponseServerError("Bad file format, please let us know.")

  try:
    key = request.POST["key"]
  except KeyError:
    fail(ip)
    return HttpResponseBadRequest("Need `key` in post data.")

  # Check key
  if hash(key) == article["key"]:
    os.remove(path)
    return HttpResponse(f"Article {id} deleted.")
  else:
    fail(ip)
    return HttpResponseBadRequest("Wrong key.")
