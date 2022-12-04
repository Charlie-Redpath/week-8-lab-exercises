"""Simple docs forwarding"""

from django.shortcuts import render

def index(request):
  """Documentation page #1"""
  return render(None, "documentation.html")

def docs1():
  """Documentation page #2"""
  return render(None, "actual_documentation.html")

def docs2():
  """Documentation page #3"""
  return render(None, "actual_actual_documentation.html")

def proper_docs(request):
  """The **actual** docs"""
  return render(None, "proper_docs.html")

def docs_n(request, n: int):
  match n:
    case 1:
      return docs1()
    case 2:
      return docs2()
    case _:
      return index(request)
