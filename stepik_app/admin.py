from django.contrib import admin

from .models import Course, LessonTest, Module, Submission


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class LessonInline(admin.TabularInline):
    model = LessonTest
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "is_free", "created_at")
    list_filter = ("is_free", "created_at")
    search_fields = ("title", "description", "owner__username", "owner__email")
    ordering = ("-created_at",)
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title", "course__owner__username")
    ordering = ("course", "order")
    inlines = [LessonInline]


@admin.register(LessonTest)
class LessonTestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "module", "order")
    list_filter = ("module", "module__course")
    search_fields = ("title", "task_text", "module__title", "module__course__title")
    ordering = ("module", "order")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lesson", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "user__username",
        "lesson__title",
        "lesson__module__course__title",
        "output",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
