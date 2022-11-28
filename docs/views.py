from django.shortcuts import render

def index(request):
  return render(None, "documentation.html")

def docs1():
  return render(None, "actual_documentation.html")

def docs2():
  return render(None, "actual_actual_documentation.html")

def docs_n(request, n: int):
  match n:
    case 1:
      return docs1()
    case 2:
      return docs2()
