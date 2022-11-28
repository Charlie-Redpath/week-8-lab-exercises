from django.http import HttpResponseBadRequest

def index(request):
    return HttpResponseBadRequest("This url is not functional. Use either /docs or /API")
