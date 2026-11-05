from django.urls import path

from questions import views

urlpatterns = [
    path('login/', views.IndexView.as_view(), name='login'),
    path('signup/', views.IndexView.as_view(), name='signup'),
]
