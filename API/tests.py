import re
import json
import time

from django.test import RequestFactory
from .views import get_article, post_article, MAX_FAIL, MIN_SEP

# Setup testing
DATA = {
    "title": "TEST ARTICLE",
    "sub_heading": "",
    "content": "This is a test article."
}

factory = RequestFactory()

# Test posting article
req = factory.post("/API/article", DATA)
resp = post_article(req, bypass_limits=True)

assert resp.status_code == 200

# Test getting an article (0 will always exist)
req2 = factory.get("/API/article/")
resp = get_article(req2, 0, bypass_limits=True)
resp_data = json.loads(resp.content)

assert all(
    i in DATA for i in ["title", "sub_heading", "content"]
)

# Bad data
req = factory.post("/API/article", {"BAD": "DATA"})

# Test rate limiting
for _ in range(5):
    post_article(req)
else:
    resp = post_article(req)
    assert resp.status_code == 429

# Test fail limiting
for _ in range(MAX_FAIL + 1):
    time.sleep(MIN_SEP + .05)  # Avoid rate limit
    resp = post_article(req)
else:
    assert resp.status_code == 400
