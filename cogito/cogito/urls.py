"""
URL configuration for cogito project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.view_pdb, name='view_pdb'),  # Ensure this name matches your template
    path("protein/pdb/<str:pdb_id>.pdb", views.serve_pdb_file, name="serve_pdb_file"),
    path('', include("home.urls")),
    path("protein/", include("protein.urls")),  # Include your app's URLs
    path('admin/', admin.site.urls),
]
