from django.contrib import admin

from .models import Comment, Example


class ExampleAdmin(admin.ModelAdmin):
    list_display = ("text", "project", "meta","uploaded_file")
    ordering = ("project",)
    search_fields = ("text","uploaded_file",)
    list_filter = ("project","uploaded_file")


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "example",
        "text",
        "created_at",
    )
    ordering = (
        "user",
        "created_at",
    )
    search_fields = ("user",)


admin.site.register(Example, ExampleAdmin)
admin.site.register(Comment, CommentAdmin)
