from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Question, QuestionVote


class QuestionRatingTests(TestCase):
    def test_vote_matches_rating_after_reload(self):
        user = get_user_model().objects.create_user(username='voter')
        question = Question.objects.create(author=user, title='Рейтинг')
        self.client.force_login(user)
        url = reverse('question_actions:vote_question', args=[question.pk])
        for value in (1, -1, 0):
            with self.subTest(value=value):
                self.assertEqual(self.client.post(url, {'value': value}).json()['rating'], value)
                question.save()  # An older instance can still be open in the admin.
                for path in ('/', '/hot/', question.get_absolute_url()):
                    response = self.client.get(path)
                    self.assertContains(response, f'data-rating aria-live="polite">{value}</span>')

    def test_bulk_votes_and_user_deletion(self):
        users = get_user_model().objects
        author = users.create_user(username='author')
        voter = users.create_user(username='voter')
        question = Question.objects.create(author=author, title='Голоса')
        QuestionVote.objects.bulk_create([
            QuestionVote(question=question, user=user, value=1) for user in (author, voter)
        ])
        question.refresh_from_db()
        self.assertEqual(question.rating, 2)
        voter.delete()
        question.refresh_from_db()
        self.assertEqual(question.rating, 1)
