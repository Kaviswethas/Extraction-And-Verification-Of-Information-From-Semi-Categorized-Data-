from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.login,name='login'),
    path('register/', views.register, name='register'),
    path('application-form/', views.index,name='index'),
    path('verify_form/', views.verify_form, name='verify_form'),  
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('sa_login/', views.sa_login, name='sa_login'),
    path('sa_dashboard/', views.sa_dashboard, name='sa_dashboard'),
    path('sa_logout/', views.sa_logout, name='sa_logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path("view_applicants/", views.view_applicants, name="view_applicants"),
    path("download_pdf/<str:user_id>/", views.download_pdf, name="download_pdf"),
    path("block_applicant/", views.block_applicant, name="block_applicant"),
    path('applicant_queries/',views.applicant_queries,name='applicant_queries'),
    path('update_resolved_status/', views.update_resolved_status, name='update_resolved_status'),
    path('get_contacts_data/', views.get_contacts_data, name='get_contacts_data'),
    path('blocked_applicants/',views.blocked_applicants,name='blocked_applicants'),
    path('add_reports/',views.add_reports,name='add_reports'),
    path('contact/',views.contact,name='contact'),
    path('create_admin',views.create_admin, name='create_admin'),
    path('update_admin',views.update_admin, name='update_admin'),
    path('delete_admin',views.delete_admin, name='delete_admin'),
    path('view_reports/',views.view_reports,name='view_reports'),
    path('admin_list/',views.admin_list,name='admin_list'),
    path('chat/', views.chat, name='chat'),
    path('logout/', views.user_logout, name='user_logout'),
    path('submit-application-form/', views.submit_application_form, name='submit_application_form'),
    path('success/',views.success,name='success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)