import re
import json

from django.test import RequestFactory
from .views import get_article, post_article

# Setup testing
DATA = {
    "title": "TEST ARTICLE",
    "sub_heading": "",
    "content": "This is a test article."
}

factory = RequestFactory()

# Test posting article
req = factory.post("/API/article", DATA)
resp = post_article(req)

assert resp.status_code == 200

# Get id from response
id = re.findall(r"(?<=#)\d+", str(resp.content))[0]
req2 = factory.get(f"/API/article/")
resp = get_article(req2, id)

resp_data = json.loads(resp.content)

assert all(
    resp_data[i] == DATA[i] for i in ["title", "sub_heading", "content"]
)
