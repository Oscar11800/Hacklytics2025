from django.urls import path
from . import views

urlpatterns = [
    # path('docking/', views.docking_graph, name='docking_graph'),
    path("pdb/<str:pdb_id>.pdb/", views.serve_pdb_file, name="serve_pdb_file"),
    path("view/", views.view_pdb, name="view_pdb"),  # Remove <str:pdb_id> from the URL pattern
]