from django.urls import path
from . import views

app_name = 'innovation'

urlpatterns = [
    path('', views.idea_list, name='list'),
    path('new/', views.idea_create, name='create'),
    path('<int:idea_id>/', views.idea_detail, name='detail'),
    path('<int:idea_id>/vote/', views.idea_vote_toggle, name='vote'),
]
