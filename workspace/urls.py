from django.urls import path

from workspace import views

urlpatterns = [
    path('', views.firstpage),
    path('logout/', views.logout),
    path('create/', views.create),
    path('myreturn/', views.my_create_return),
    path('create_labels/', views.create_labels),
    path('create_suc/', views.createsuc),
    path('imgupload/', views.imgupload),
    path('videoupload/', views.videoupload),
    path('chakan/create/', views.chakan_create),
    path('chakan/myallow/', views.chakan_allow),
    path('chakan/project/', views.chakan_project),
    path('chakan/download/', views.download),
    path('chakan/', views.chakan),
    path('receive/', views.receive),
    path('work/', views.work),
]