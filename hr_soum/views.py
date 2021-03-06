import os
import json
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
from django.forms import formset_factory
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import send_mail, EmailMessage
from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import *
from .models import *
from rest_framework import generics
from . import serializers
from .chart_data import *

import datetime
from django.utils.formats import localize
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime
from chartit import DataPool, Chart
from django.shortcuts import render_to_response
from rolepermissions.decorators import has_role_decorator
from rolepermissions.roles import assign_role
from django.contrib.auth.decorators import permission_required
from rolepermissions.checkers import has_object_permission, has_permission

from django.contrib.auth.hashers import make_password
from math import *

class RegistrationView(generic.CreateView):
    form_class = RegistrationForm
    form_valid_message = _('you have successfully signed up')
    success_url = reverse_lazy('login')
    model = Employe
    template_name = 'hr_soum/register.html'



class LoginView(generic.FormView):
    form_class = LoginForm
    form_valid_message = 'you are logged in'
    model = Employe
    success_url = reverse_lazy('acceuil')
    template_name = 'hr_soum/login.html'

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            self.request.user.is_agency = False

            url = reverse('acceuil')
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model."
                )
        return url

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super().form_valid(locals())
        else:
            return self.form_invalid(locals())


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def delete_user(request, user_id):
    user = Employe.objects.get(id=user_id)

    context = {'user': user.get_full_name()}
    html_content = render_to_string('mails/user_account_delete.html', context)

    # mail = SentMail()
    # mail.full_name = request.user.get_full_name()
    # mail.title = _('Account Deleted')
    # mail.email = user.email
    # mail.message = html_content
    # mail.save()

    user.delete()
    messages.success(request, _('Account succesfully deleted'))
    return redirect('users')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, _('Your password was Successfully Updated!'))
            return redirect('acceuil')
        else:
            messages.error(request, _('Please correct the errors below!'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'hr_soum/change_password.html', {
        'form': form
        })

@login_required
def user_profile(request, user_id):
    user = Employe.objects.get(id=user_id)
    fonctions = Fonction.objects.all()
    departments = Departement.objects.all()

    return render(request, 'hr_soum/user_profile.html', {'users': user, 'departments': departments, 'fonctions': fonctions, 'genders': GENRE_CHOICES})

@login_required
def update_user_profile(request, user_id):
    if request.method == 'POST':
        user = Employe.objects.get(id=user_id)

        user.email = request.POST.get('email', None)
        user.first_name = request.POST.get('first_name', None)
        user.last_name = request.POST.get('last_name', None)
        user.phone1 = request.POST.get('phone1', '')
        user.phone2 = request.POST.get('phone2', '')
        user.address = request.POST.get('address', None)
        user.genre = request.POST.get('gender', None)

        user.save()
        messages.success(request, _('Your Profil has been updated succesfully'))
        return redirect('acceuil')

        user.save()

    else:
        return redirect('user_profile', user.id)

@login_required
def register(request):
    form = EmployeForm()

    if request.method == 'POST':
        form = EmployeForm(request.POST)

        if form.is_valid():
            empoly = Employe()
            

            empoly.matricule = form.cleaned_data['matricule']
            empoly.first_name = form.cleaned_data['first_name']
            empoly.last_name = form.cleaned_data['last_name']
            empoly.email = form.cleaned_data['email']
            empoly.genre = form.cleaned_data['genre']
            empoly.fonction = form.cleaned_data['fonction']
            empoly.departement = form.cleaned_data['departement']
            empoly.phone1 = form.cleaned_data['phone1']
            empoly.phone2 = form.cleaned_data['phone2']
            empoly.address = form.cleaned_data['address']

            empoly.set_password('1234')

            empoly.save()
            
            assign_role(empoly,'employer')

            for typ in Type_conge.objects.all():

                conge = Conge()
                
                conge.employe = Employe.objects.last()
                conge.type_conge = typ
                conge.nombre_jour = 0
                
                conge.save()

            messages.success(request, 'Vous avez bien ajouté un employé')
            return redirect('employees')
            
        else:
            print("not valid")

    return render(request, 'hr_soum/employe.html', {'form':form})

def employe_details(request, emp_id):

    employ = Employe.objects.get(id=emp_id)
    try:
        conges = Conge.objects.filter(employe=employ)
    except Conge.DoesNotExist:
        conges = None

    return render(request, 'hr_soum/employe_details.html', {'employ':employ, 'conges':conges})

@login_required
def list_employ(request):
    all_user = Employe.objects.all()

    return render(request, 'hr_soum/list_employees.html', {'all_user':all_user})

@login_required
def updateEmploye(request,emp_id):
    employ = get_object_or_404(Employe, pk=emp_id)
    form = UpdateEmployForm(employ.matricule, employ.first_name, employ.last_name, employ.fonction, employ.departement, employ.phone1, employ.phone2, employ.address, employ.email, employ.genre)
    if request.method == 'POST':
        
        fonct = Fonction.objects.get(id=request.POST.get('fonction'))
        depar = Departement.objects.get(id=request.POST.get('departement'))
        employ.matricule = request.POST.get('matricule')
        employ.first_name = request.POST.get('first_name')
        employ.last_name = request.POST.get('last_name')
        employ.email = request.POST.get('email')
        employ.genre = request.POST.get('genre')
        employ.fonction = fonct
        employ.departement = depar
        employ.phone1 = request.POST.get('phone1')
        employ.phone2 = request.POST.get('phone2')
        employ.address = request.POST.get('address')

        employ.save()

        messages.success(request, 'Vous avez bien modifié l\'employé')

    
        return redirect('employees')

    return render(request, 'hr_soum/update_employe.html', {'form':form})
"""
@login_required
def register(request):
    form = EmployeForm()

    if request.method == 'POST':
        form = EmployeForm(request.POST)
        typ_conge = Type_conge.objects.all()

        if form.is_valid():

            try:
                manager = Employe.objects.get(departement_id=form.cleaned_data['departement'], is_manager=True)
            except Employe.DoesNotExist:
                manager = None

            empoly = Employe()
            

            empoly.matricule = form.cleaned_data['matricule']
            empoly.first_name = form.cleaned_data['first_name']
            empoly.last_name = form.cleaned_data['last_name']
            empoly.email = form.cleaned_data['email']
            empoly.genre = form.cleaned_data['genre']
            empoly.fonction = form.cleaned_data['fonction']
            empoly.departement = form.cleaned_data['departement']
            empoly.phone1 = form.cleaned_data['phone1']
            empoly.phone2 = form.cleaned_data['phone2']
            empoly.address = form.cleaned_data['address']

            if manager:
                empoly.id_manager = manager.matricule
                empoly.save()
            else:
                empoly.save()

            for typ in Type_conge.objects.all():

                conge = Conge()
                
                conge.employe = Employe.objects.last()
                conge.type_conge = typ
                conge.nombre_jour = 0
                print(typ.indice)
                conge.save()
                print("end save")

            messages.success(request, 'Vous avez bien ajouté un employé')
            return redirect('employees')
            
        else:
            print("not valid")

    return render(request, 'hr_soum/employe.html', {'form':form})
"""


@login_required
def user_account(request, user_id):
    company = User.objects.get(id=user_id)
    missions = Mission.objects.all()

    return render(request, 'hr_soum/user_account.html', {
        'user': company,
        'missions': missions
    })

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        elif request.META.get('HTTP_X_REAL_IP'):
            ip = request.META.get('HTTP_X_REAL_IP')
        else:
            ip = request.META.get('REMOTE_ADDR')
    except:
        ip = ""
    return ip

def create_success(request):
    return render(request, 'hr_soum/create_success.html',)
    

@login_required
def delete_user(request, user_id):
    if request.user.is_admin:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, _('Account succesfully deleted'))
        return redirect('users')
        


@login_required
def add_department(request):
   
    form = DepartementForm(request.POST or None)

    try:
        departement = Departement.objects.all()
    except expression as identifier:
        pass 

    if request.method == "POST":
        
        if form.is_valid():
            name = form.cleaned_data['name']            
            departement = Departement()
            departement.name = name
            departement.save()

            return redirect('department')
    return render(request, 'hr_soum/liste_departments.html', {'form': form, 'departements': departement})

@login_required
def add_function(request):

    form = FonctionForm(request.POST or None)

    try:
        fonction = Fonction.objects.all()
    except expression as identifier:
        pass 

    if request.method == "POST":
        
        if form.is_valid():
            name = form.cleaned_data['name']
            fonction = Fonction()
            fonction.name = name
            fonction.save()

            return redirect('function')
    return render(request, 'hr_soum/liste_functions.html', {'form': form, 'fonctions': fonction})


@login_required
def acceuil(request):
    return render(request, 'hr_soum/acceuil.html',)

@login_required
def delete_function(request, delete_id):
    try:
        fonction = Fonction.objects.get(id=delete_id)
        fonction.delete()
        return redirect('function')
    except expression as identifier:
        pass

@login_required
def delete_department(request, department_id):
    try:
        departement = Departement.objects.get(id=department_id)
        departement.delete()
        return redirect('department')
    except expression as identifier:
        pass

@login_required
def update_function(request, function_id):
    try:
        fonction = Fonction.objects.get(id=function_id)
        form = FonctionForm(request.POST)
        if request.method == 'POST':
            if form.is_valid():
                name = form.cleaned_data['name']
                fonction.name = name
                fonction.save()

                return redirect('function')
    except expression as identifier:
        pass


@login_required
def update_departement(request, departement_id):
    try:
        departement = Departement.objects.get(id=departement_id)
        form = DepartementForm(request.POST)
        if request.method == 'POST':
            if form.is_valid():
                name = form.cleaned_data['name']
                departement.name = name
                departement.save()

                return redirect('department')
    except expression as identifier:
        pass

@login_required
def add_manager(request, employ_id):
    try:
        employ = Employe.objects.get(id=employ_id)
        employ.is_manager = True
        employ.save()

        employ_dep = Employe.objects.filter(departement_id=employ.departement_id)

        for employs in employ_dep:
            employs.id_manager = employ.matricule
            employs.save()

        return redirect('employe_details', employ_id)
    except Employe.DoesNotExist:
        pass

@login_required
def delete_manager(request, employ_id):
    try:
        employ = Employe.objects.get(id=employ_id)
        employ.is_manager = False
        employ.save()

        employ_dep = Employe.objects.filter(departement_id=employ.departement_id)

        for employs in employ_dep:
            employs.id_manager = None
            employs.save()

        return redirect('employe_details', employ_id)
    except Employe.DoesNotExist:
        pass
