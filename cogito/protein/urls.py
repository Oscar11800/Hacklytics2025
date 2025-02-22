from django.urls import path
from . import views

urlpatterns = [
    path('docking/', views.docking_graph, name='docking_graph'),
    path('fetch_pdb/<str:pdb_id>/', views.fetch_pdb, name='fetch_pdb'),
    path('visual/', views.visual, name='visual'),
]