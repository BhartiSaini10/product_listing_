from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('myntra/men-tshirts', views.GetMensTshirts.as_view()),
]