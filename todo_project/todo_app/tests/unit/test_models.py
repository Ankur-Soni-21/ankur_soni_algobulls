# todo_app/tests/unit/test_models.py

from django.test import TestCase
from todo_app.models import Task, Tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class TaskModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag')
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            due_date=timezone.now() + timedelta(days=1),
            status='OPEN'
        )
        self.task.tags.add(self.tag)

    def test_task_str(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_tag_str(self):
        self.assertEqual(str(self.tag), 'Test Tag')

    def test_due_date_not_in_past(self):
        past_due_date = timezone.now() - timedelta(days=1)
        task = Task(
            title='Past Task',
            description='This task has a past due date HEHE',
            due_date=past_due_date,
            status='OPEN'
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_clean_method(self):
        future_due_date = timezone.now() + timedelta(days=5)
        self.task.due_date = future_due_date
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_task_with_no_due_date(self):
        self.task.due_date = None
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly when due_date is None!")
