from django.shortcuts import render
from api.models import Take

def index(request):
    take = Take.objects.all().last()
    filetype = ""
    if take:
        if take.location.endswith(".wav"):
            filetype = "wav"
        elif take.location.endswith(".mp3"):
            filetype = "mpeg"
    return render(request, 'index.html', {"lasttake": take, "filetype": filetype})
