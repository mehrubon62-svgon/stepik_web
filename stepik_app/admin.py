from django.contrib import admin

from .models import Course, LessonTest, Module, Submission

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(LessonTest)
admin.site.register(Submission)
