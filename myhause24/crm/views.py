from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import House
from .forms import HouseForm

# Create your views here.


class HouseListView(ListView):
    model = House
    template_name = 'crm/pages/houses/list_houses.html'


class HouseCreateView(CreateView):
    model = House
    template_name = 'crm/pages/houses/create_house.html'
    form_class = HouseForm


@login_required(login_url='login')
def index(request):
    return render(request, 'crm/pages/index.html')