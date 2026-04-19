from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonTestViewSet, ModuleViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"lessons", LessonTestViewSet, basename="lesson")
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = [
    path("", include(router.urls)),
]
