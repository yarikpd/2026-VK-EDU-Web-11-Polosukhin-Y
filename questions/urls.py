from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ask/', views.AskView.as_view(), name='ask'),
    path('question/<int:id>/', views.QuestionView.as_view(), name='question'),
]