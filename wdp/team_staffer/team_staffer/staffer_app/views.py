from django.shortcuts import render
from .models import Staffer

def home(request):
    staffers_list = Staffer.objects.all()
    return render(request, 'home.html', {"staffers":staffers_list})
