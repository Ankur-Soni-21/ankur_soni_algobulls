from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from todo_app.models import Task, Tag
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import base64


class TaskAPITestCase(APITestCase):
    def setUp(self):
        # Create a user for authentication
        self.username = "an211"
        self.password = "Soni4680"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

        # Initialize the test client
        self.client = APIClient()

        # Set Basic Auth credentials
        credentials = f"{self.username}:{self.password}"
        token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        self.client.credentials(HTTP_AUTHORIZATION="Basic " + token)

        # Create tags
        self.tag1 = Tag.objects.create(name="Work")
        self.tag2 = Tag.objects.create(name="Urgent")

        # Create a task
        self.task = Task.objects.create(
            title="Existing Task",
            description="This is an existing task",
            due_date=timezone.now() + timedelta(days=2),
            status="OPEN",
        )
        self.task.tags.add(self.tag1)

    def test_create_task(self):
        url = reverse("task-create")
        data = {
            "title": "New Task",
            "description": "This is a new task",
            "due_date": (timezone.now() + timedelta(days=1)).isoformat(),
            "status": "OPEN",
            "tags": [{"name": "Work"}, {"name": "Home"}],
        }
        response = self.client.post(url, data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.last().title, "New Task")

    def test_task_str_method(self):
        self.assertEqual(str(self.task), "Existing Task")

    def test_tag_str_method(self):
        self.assertEqual(str(self.tag1), "Work")

    def test_read_all_tasks(self):
        url = reverse("task-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_read_single_task(self):
        url = reverse("task-detail", kwargs={"pk": self.task.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Existing Task")

    def test_update_task_with_tags(self):
        url = reverse("task-update", kwargs={"pk": self.task.pk})
        data = {
            "title": "Updated Task with Tags",
            "description": "Updated description",
            "status": "WORKING",
            "tags": [{"name": "Urgent"}, {"name": "High Priority"}],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task with Tags")
        self.assertEqual(self.task.status, "WORKING")
        self.assertEqual(self.task.tags.count(), 2)
        tag_names = [tag.name for tag in self.task.tags.all()]
        self.assertIn("Urgent", tag_names)
        self.assertIn("High Priority", tag_names)

    def test_delete_task(self):
        url = reverse("task-delete", kwargs={"pk": self.task.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_due_date_validation(self):
        url = reverse("task-create")
        data = {
            "title": "Invalid Task",
            "description": "This task has an invalid due date",
            "due_date": (timezone.now() - timedelta(days=1)).isoformat(),
            "status": "OPEN",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)

    def test_unauthenticated_access(self):
        # Remove authentication credentials
        self.client.credentials()  # This clears any existing credentials
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
