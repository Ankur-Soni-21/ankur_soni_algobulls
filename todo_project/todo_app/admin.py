# Notes:

# readonly_fields to prevent editing of timestamp.
# fieldsets to organize fields in the admin form.
# list_filter to add filters in the admin list view.


from django.contrib import admin
from .models import Task, Tag


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "due_date", "timestamp")
    list_filter = ("status", "due_date", "tags")
    search_fields = ("title", "description")
    fieldsets = (
        (None, {"fields": ("title", "description", "status")}),
        (
            "Optional Information",
            {
                "classes": ("collapse",),
                "fields": ("due_date", "tags"),
            },
        ),
    )
    readonly_fields = ("timestamp",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
