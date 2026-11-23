from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ask/', views.AskView.as_view(), name='ask'),
    path('question/<int:id>/', views.QuestionView.as_view(), name='question'),
    path('hot/', views.HotView.as_view(), name='hot'),
    path('tag/<path:tag>/', views.TagView.as_view(), name='tag'),
    path('actions/', include('questions.action_urls')),
]
