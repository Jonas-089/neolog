from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('alle/', WordListView.as_view(), name='all-words'),
    path('', views.home, name='homepage'),
    #path('alle/', views.all_words, name='all-words'),
    path('buchstabe/<str:route>/', views.letter_view, name='letter-words'),
    path('wort/<str:word>/', WordView, name='one-word'),
    path('definition/neu/', DefinitionCreateView.as_view(), name='create-definition'),
    path('definition/<int:pk>/', DefinitionDetailView.as_view(), name='definition-detail'),
    path('about/', views.about, name='blog-about'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('like/<int:pk>/', like_definition, name="like-definition"),
    path('dislike/<int:pk>/', dislike_definition, name="dislike-definition"),

]
