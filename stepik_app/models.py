from django.conf import settings
from django.db import models


class Course(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course_id}: {self.title}"


class LessonTest(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    task_text = models.TextField()
    expected_output = models.TextField()
    starter_code = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("module", "order")

    def __str__(self):
        return self.title


class Submission(models.Model):
    class Status(models.TextChoices):
        TESTED = "tested", "Tested"
        CORRECT = "correct", "Correct"
        WRONG = "wrong", "Wrong"
        ERROR = "error", "Error"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    lesson = models.ForeignKey(LessonTest, on_delete=models.CASCADE, related_name="submissions")
    code = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Submission<{self.user_id}:{self.lesson_id}:{self.status}>"
