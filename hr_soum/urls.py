from django.conf.urls import url, include
from .views import (
    LoginView,
    RegistrationView,
    logout_view,
    user_profile,
    update_user_profile,
    change_password,
    create_success,
    delete_user,
    add_department,
    add_function,
    delete_function,
    delete_department,
    update_function,
    update_departement,
    acceuil,
    register,
    list_employ,
    updateEmploye,
    employe_details,
    add_manager,
    delete_manager
    )

urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^enregistrement/$', RegistrationView.as_view(), name='register'),
    url(r'^deconnection/$', logout_view, name='logout'),
    url(r'^mon-profile/(?P<user_id>[0-9]+)/$', user_profile, name='user_profile'),
    url(r'^mise-a-jour-des-informations-de-l-utilisateur/(?P<user_id>[0-9]+)$', update_user_profile, name='update_user'),
    url(r'^suppression-de-l-utilisateur/(?P<user_id>[0-9]+)$', delete_user, name='delete_user'),
    url(r'^changement-de-mot-de-passe/$', change_password, name='change_password'),
    url(r'^creation-avec-success/$', create_success, name='create_success'),
    url(r'^add-department/$', add_department, name='department'),
    url(r'^delete-function/(?P<delete_id>[0-9]+)$', delete_function, name='delete_function'),
    url(r'^add-function/$', add_function, name='function'),
    url(r'^delete-department/(?P<department_id>[0-9]+)$', delete_department, name='delete_department'),

    url(r'^update-function/(?P<function_id>[0-9]+)$', update_function, name='update_function'),
    url(r'^update-departement/(?P<departement_id>[0-9]+)$', update_departement, name='update_departement'),

    url(r'^add-manager/(?P<employ_id>[0-9]+)$', add_manager, name='add_manager'),
     url(r'^delete-manager/(?P<employ_id>[0-9]+)$', delete_manager, name='delete_manager'),
    
    

    url(r'^acceuil/$', acceuil, name='acceuil'),
    url(r'^register/$', register, name='register'  ),
    url(r'^list_employe/$', list_employ, name='employees'),   
    url(r'^update_employe/(?P<emp_id>[0-9]+)$', updateEmploye, name='update_employe'),
    url(r'^employe_details/(?P<emp_id>[0-9]+)$', employe_details, name='employe_details')
    
]
