# serializers.py

from rest_framework import serializers
from .models import Task, Tag
from django.utils import timezone

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        extra_kwargs = {
            'name': {'validators': []},  # Remove the default uniqueness validator
        }

class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'timestamp', 'title', 'description', 'due_date', 'tags', 'status']
        read_only_fields = ('timestamp',)

    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        task = Task(**validated_data)
        task.full_clean()  # Call full_clean to trigger model validation
        task.save()
        self._create_or_update_tags(task, tags_data)
        return task

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()  # Call full_clean to trigger model validation
        instance.save()
        if tags_data:
            self._create_or_update_tags(instance, tags_data)
        return instance

    def _create_or_update_tags(self, task, tags_data):
        tag_objs = []
        for tag_data in tags_data:
            tag_name = tag_data.get('name')
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag_objs.append(tag)
        task.tags.set(tag_objs)
        
