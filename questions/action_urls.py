from django.urls import path

from . import views
from .models import Answer, Question

app_name = 'question_actions'

urlpatterns = [
    path('question/<int:id>/vote/', views.VoteView.as_view(model=Question), name='vote_question'),
    path('answer/<int:id>/vote/', views.VoteView.as_view(model=Answer), name='vote_answer'),
    path('question/<int:id>/accepted/', views.AcceptedAnswerView.as_view(), name='accept_answer'),
]
