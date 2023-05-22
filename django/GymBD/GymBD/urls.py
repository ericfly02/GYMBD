"""
URL configuration for GymBD project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from gym import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ciutats/', views.ciutats, name='ciutats'),
    path('empleats/', views.empleats, name='empleats'),
    path('gimnasos/', views.gimnasos, name='gimnasos'),
    path('treballadors/', views.treballadors, name='treballadors'),
    path('sales/', views.sales, name='sales'),
    path('classes/', views.classes, name='classes'),
    path('dies/', views.dies, name='dies'),
    path('aliments/', views.aliments, name='aliments'),
    path('dietes/', views.dietes, name='dietes'),
    path('rutines/', views.rutines, name='rutines'),
    path('clients/', views.clients, name='clients'),
    path('pagaments/', views.pagaments, name='pagaments'),
    path('quantificadors_dietes/', views.quantificadors_dietes, name='quantificadors_dietes'),
    path('quantificadors_pesos/', views.quantificadors_pesos, name='quantificadors_pesos'),
    path('apats/', views.apats, name='apats'),
    path('franges_horaries/', views.franges_horaries, name='franges_horaries'),
    path('quantitats_aliments/', views.quantitats_aliments, name='quantitats_aliments'),
    path('exercicis/', views.exercicis, name='exercicis'),
    path('entrenaments/', views.entrenaments, name='entrenaments'),
    path('entrenaments_diaris/', views.entrenaments_diaris, name='entrenaments_diaris'),
    path('entrenaments_personals/', views.entrenaments_personals, name='entrenaments_personals'),
    path('rondes/', views.rondes, name='rondes'),
    path('series/', views.series, name='series'),
    path('realitza_exercicis/', views.realitza_exercicis, name='realitza_exercicis'),
    path('participacions/', views.participacions, name='participacions'),
]



