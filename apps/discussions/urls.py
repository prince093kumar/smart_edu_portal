from django.urls import path
from . import views

app_name = 'discussions'

urlpatterns = [
    path('<slug:course_slug>/', views.thread_list, name='list'),
    path('<slug:course_slug>/new/', views.create_thread, name='create'),
    path('<slug:course_slug>/thread/<int:thread_id>/', views.thread_detail, name='detail'),
]
