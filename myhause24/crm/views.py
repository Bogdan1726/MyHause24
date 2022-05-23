from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, FormView, DetailView
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from .models import House, Section, Floor
from .forms import HouseForm, SectionForm, FloorForm, UserFormSet
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.


class HouseListView(ListView):
    model = House
    template_name = 'crm/pages/houses/list_houses.html'
    context_object_name = 'houses'

    def get_queryset(self):
        return self.model.objects.order_by('id')


class HouseDetailView(DetailView):
    model = House
    template_name = 'crm/pages/houses/detail_house.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super(HouseDetailView, self).get_context_data()
        context['section'] = Section.objects.filter(house=self.object)
        context['floor'] = Floor.objects.filter(house=self.object)
        return context


def load_role(request):
    if request.is_ajax():
        user_id = request.GET.get('user')
        role = User.objects.filter(id=user_id).values('role__name')
        response = {
            'role': list(role)
        }
        return JsonResponse(response, status=200)
    return HttpResponse()


class HouseUpdateView(UpdateView):
    model = House
    template_name = 'crm/pages/houses/update_house.html'
    form_class = HouseForm
    formset_for_section = modelformset_factory(Section, form=SectionForm, extra=0, can_delete=True)
    formset_for_floor = modelformset_factory(Floor, form=FloorForm, extra=0, can_delete=True)
    formset_for_user = formset_factory(form=UserFormSet, extra=0, can_delete=True)

    def get_success_url(self):
        return reverse_lazy('detail_house', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(HouseUpdateView, self).get_context_data()
        context['formset_for_section'] = self.formset_for_section(
            self.request.POST or None,
            queryset=Section.objects.filter(house=self.object),
            prefix='section'
        )
        context['formset_for_floor'] = self.formset_for_floor(
            self.request.POST or None,
            queryset=Floor.objects.filter(house=self.object),
            prefix='floor'
        )
        context['formset_for_user'] = self.formset_for_user(
            self.request.POST or None,
            initial=[{'user': x, 'role': x.role, 'id': x.id} for x in self.object.user.all().order_by('house')],
            prefix='user'
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset_for_section = context['formset_for_section']
        formset_for_floor = context['formset_for_floor']
        formset_for_user = context['formset_for_user']
        if formset_for_section.is_valid() and formset_for_floor.is_valid() and formset_for_user.is_valid():
            house = form.save()
            for section in formset_for_section:
                if section.cleaned_data:
                    if section.is_valid():
                        section = section.save(commit=False)
                        section.house = house
                        section.save()
            formset_for_section.save()
            for floor in formset_for_floor:
                if floor.cleaned_data:
                    if floor.is_valid():
                        floor = floor.save(commit=False)
                        floor.house = house
                        floor.save()
            formset_for_floor.save()
            house.user.clear()
            for form_user in formset_for_user:
                if form_user.cleaned_data and form_user.cleaned_data['DELETE'] is False:
                    if form_user.is_valid():
                        user = form_user.cleaned_data.get('user')
                        house.user.add(user)
            house.save()
            return super().form_valid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class HouseCreateView(CreateView):
    model = House
    template_name = 'crm/pages/houses/create_house.html'
    form_class = HouseForm
    formset_for_section = modelformset_factory(Section, form=SectionForm, extra=0, can_delete=True)
    formset_for_floor = modelformset_factory(Floor, form=FloorForm, extra=0, can_delete=True)
    formset_for_user = formset_factory(form=UserFormSet, extra=0, can_delete=True)

    def get_success_url(self):
        return reverse_lazy('detail_house', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(HouseCreateView, self).get_context_data()
        context['formset_for_section'] = self.formset_for_section(
            self.request.POST or None,
            queryset=Section.objects.none(),
            prefix='section'
        )
        context['formset_for_floor'] = self.formset_for_floor(
            self.request.POST or None,
            queryset=Floor.objects.none(),
            prefix='floor'
        )
        context['formset_for_user'] = self.formset_for_user(
            self.request.POST or None,
            prefix='user'
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset_for_section = context['formset_for_section']
        formset_for_floor = context['formset_for_floor']
        formset_for_user = context['formset_for_user']
        if formset_for_section.is_valid() and formset_for_floor.is_valid() and formset_for_user.is_valid():
            house = form.save()
            for section in formset_for_section:
                if section.cleaned_data:
                    if section.is_valid():
                        section = section.save(commit=False)
                        section.house = house
                        section.save()
            formset_for_section.save()
            for floor in formset_for_floor:
                if floor.cleaned_data:
                    if floor.is_valid():
                        floor = floor.save(commit=False)
                        floor.house = house
                        floor.save()
            for form_user in formset_for_user:
                if form_user.cleaned_data and form_user.cleaned_data['DELETE'] is False:
                    user = form_user.cleaned_data.get('user')
                    house.user.add(user)
            house.save()
            return super().form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


@login_required(login_url='login')
def index(request):
    return render(request, 'crm/pages/index.html')
