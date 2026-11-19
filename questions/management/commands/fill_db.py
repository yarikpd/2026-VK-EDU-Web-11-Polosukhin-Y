# This file was created entirely by AI, as I simply don’t have enough time to do it myself.
# TODO: rewrite it by myself

from itertools import batched, count, islice
from random import choice, randint, sample

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from faker import Faker

from core.models import Profile
from questions.management.seed_content import DISCUSSIONS, REPLY_NOTES
from questions.models import Answer, AnswerVote, Question, QuestionVote, Tag


BATCH_SIZE = 5000
ANSWERS_PER_QUESTION = 10


def create_in_batches(model, rows, *, collect_ids=False):
    ids = []
    for batch in batched(rows, BATCH_SIZE):
        created = model.objects.bulk_create(batch)
        if collect_ids:
            ids.extend(row.pk for row in created)
    return ids


def create_votes(model, target_field, target_ids, user_ids, count):
    votes_per_target, extra_votes = divmod(count, len(target_ids))

    def rows():
        for index, target_id in enumerate(target_ids):
            count_for_target = votes_per_target + (index < extra_votes)
            # Sampling without replacement keeps each target/user pair unique.
            for user_id in sample(user_ids, count_for_target):
                yield model(
                    **{target_field: target_id},
                    user_id=user_id,
                    value=choice((-1, 1)),
                )

    create_in_batches(model, rows())


def generate_users(fake, user_model, ratio):
    usernames = set(user_model.objects.values_list('username', flat=True))
    unusable_password = make_password(None)
    name_providers = (
        (fake.first_name_female, fake.last_name_female),
        (fake.first_name_male, fake.last_name_male),
    )
    for _ in range(ratio):
        base_username = fake.user_name()
        username = base_username
        suffix = 2
        while username in usernames:
            username = f'{base_username}_{suffix}'
            suffix += 1
        usernames.add(username)
        first_name, last_name = choice(name_providers)
        yield user_model(
            username=username,
            email=f'{username}@{fake.safe_domain_name()}',
            first_name=first_name(),
            last_name=last_name(),
            password=unusable_password,
        )


def generate_tag_names():
    existing = set(Tag.objects.values_list('name', flat=True))
    # Offer one recognizable tag per topic before its narrower variants.
    tags = [
        (discussion, discussion.tags[position])
        for position in range(max(len(discussion.tags) for discussion in DISCUSSIONS))
        for discussion in DISCUSSIONS
        if position < len(discussion.tags)
    ]
    for edition in count(1):
        suffix = f'-{edition}' if edition > 1 else ''
        for discussion, tag in tags:
            name = f'{tag[:30 - len(suffix)]}{suffix}'
            if name not in existing:
                existing.add(name)
                yield discussion, name


def choose_tags(tag_ids):
    other_positions = sample(range(1, len(tag_ids)), randint(0, min(2, len(tag_ids) - 1)))
    return [tag_ids[0], *(tag_ids[position] for position in other_positions)]


def generate_answers(question_ids, discussions, user_ids):
    questions_with_accepted_answer = set(sample(question_ids, len(question_ids) // 3))
    for question_id, discussion in zip(question_ids, discussions, strict=True):
        accepted_position = None
        if question_id in questions_with_accepted_answer:
            accepted_position = randint(0, ANSWERS_PER_QUESTION - 1)
        replies = islice(
            ((reply, note) for note in REPLY_NOTES for reply in discussion.replies),
            ANSWERS_PER_QUESTION,
        )
        for position, (reply, note) in enumerate(replies):
            yield Answer(
                question_id=question_id,
                author_id=choice(user_ids),
                text=f'{reply} {note}'.strip(),
                is_accepted=position == accepted_position,
            )


class Command(BaseCommand):
    help = 'Добавляет тестовые данные. Коэффициент заполнения по умолчанию — 100.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('ratio', nargs='?', type=int, default=100)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError(
                'Укажите ratio >= 2. При одном пользователе 10 вопросов и 100 ответов '
                'позволяют создать максимум 110 уникальных голосов вместо 200.'
            )
        if not connection.features.can_return_rows_from_bulk_insert:
            raise CommandError('База данных должна возвращать ID при пакетной вставке.')

        with transaction.atomic():
            self.populate(ratio)

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено: пользователей и профилей по {ratio}, тегов {ratio}, '
            f'вопросов {ratio * 10}, ответов {ratio * 100}, голосов {ratio * 200}.'
        ))

    def populate(self, ratio):
        fake = Faker('ru_RU')
        user_model = get_user_model()
        user_ids = create_in_batches(
            user_model,
            generate_users(fake, user_model, ratio),
            collect_ids=True,
        )
        create_in_batches(Profile, (Profile(user_id=user_id) for user_id in user_ids))
        tags = list(islice(generate_tag_names(), ratio))
        tag_ids = create_in_batches(
            Tag,
            (Tag(name=name) for _, name in tags),
            collect_ids=True,
        )
        tags_by_discussion = {}
        for (discussion, _), tag_id in zip(tags, tag_ids, strict=True):
            tags_by_discussion.setdefault(discussion, []).append(tag_id)

        topics = list(tags_by_discussion)
        repeats = (10 + len(topics) - 1) // len(topics)
        discussions = [
            discussion
            for _ in range(ratio)
            for discussion in (sample(topics, len(topics)) * repeats)[:10]
        ]
        question_ids = create_in_batches(
            Question,
            (
                Question(
                    author_id=choice(user_ids),
                    title=choice(discussion.titles),
                    text=discussion.text,
                )
                for discussion in discussions
            ),
            collect_ids=True,
        )
        question_tag = Question.tags.through
        create_in_batches(
            question_tag,
            (
                question_tag(question_id=question_id, tag_id=tag_id)
                for question_id, discussion in zip(question_ids, discussions, strict=True)
                for tag_id in choose_tags(tags_by_discussion[discussion])
            ),
        )
        answer_ids = create_in_batches(
            Answer,
            generate_answers(question_ids, discussions, user_ids),
            collect_ids=True,
        )

        # Split votes evenly when possible, moving excess question votes to answers.
        question_votes = min(ratio * 100, len(question_ids) * len(user_ids))
        create_votes(QuestionVote, 'question_id', question_ids, user_ids, question_votes)
        create_votes(AnswerVote, 'answer_id', answer_ids, user_ids, ratio * 200 - question_votes)
