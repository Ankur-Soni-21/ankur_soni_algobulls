# todo_app/tests/unit/test_serializers.py

from django.test import TestCase
from todo_app.models import Task, Tag
from todo_app.serializers import TaskSerializer, TagSerializer
from django.utils import timezone
from datetime import timedelta


class TagSerializerTest(TestCase):
    def test_tag_serializer_serialization(self):
        tag = Tag.objects.create(name="Test Tag")
        serializer = TagSerializer(tag)
        expected_data = {"id": tag.id, "name": "Test Tag"}
        self.assertEqual(serializer.data, expected_data)

    def test_tag_serializer_deserialization(self):
        data = {"name": "New Tag"}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, "New Tag")


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="Work")
        self.tag2 = Tag.objects.create(name="Home")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            due_date=timezone.now() + timedelta(days=1),
            status="OPEN",
        )
        self.task.tags.set([self.tag1, self.tag2])

    def test_task_serializer_serialization(self):
        serializer = TaskSerializer(self.task)
        self.assertEqual(serializer.data["title"], "Test Task")
        self.assertEqual(len(serializer.data["tags"]), 2)

    def test_task_serializer_deserialization(self):
        data = {
            "title": "New Task",
            "description": "New Description",
            "due_date": (timezone.now() + timedelta(days=2)).isoformat(),
            "status": "OPEN",
            "tags": [{"name": "Work"}, {"name": "Urgent"}],
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.title, "New Task")
        self.assertEqual(task.tags.count(), 2)

    def test_task_serializer_due_date_in_past(self):
        data = {
            "title": "Past Due Date Task",
            "description": "This task has a past due date",
            "due_date": (timezone.now() - timedelta(days=1)).isoformat(),
            "status": "OPEN",
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("due_date", serializer.errors)

    def test_task_serializer_update(self):
        data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": "WORKING",
            "tags": [{"name": "Urgent"}, {"name": "High Priority"}],
        }
        serializer = TaskSerializer(instance=self.task, data=data)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertEqual(updated_task.tags.count(), 2)
