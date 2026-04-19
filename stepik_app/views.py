import os
import subprocess
import tempfile

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Module, LessonTest, Submission
from .permissions import IsOwnerOrReadOnly
from .serializers import *


def run_python_code(code: str, timeout_sec: int = 2):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if result.returncode != 0:
            return {"ok": False, "output": stderr or "Runtime Error"}
        return {"ok": True, "output": stdout}

    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Time Limit Exceeded"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("owner").all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related("course", "course__owner").all()
    serializer_class = ModuleSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def _can_edit_course(self, course):
        return self.request.user.is_authenticated and course.owner_id == self.request.user.id

    def create(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=request.data.get("course"))
        if not self._can_edit_course(course):
            return Response({"detail": "Only course owner can add modules."}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_course(instance.course):
            return Response({"detail": "Only course owner can edit modules."}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_course(instance.course):
            return Response({"detail": "Only course owner can edit modules."}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_course(instance.course):
            return Response({"detail": "Only course owner can delete modules."}, status=403)
        return super().destroy(request, *args, **kwargs)


class LessonTestViewSet(viewsets.ModelViewSet):
    queryset = LessonTest.objects.select_related("module", "module__course", "module__course__owner").all()
    serializer_class = LessonTestSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def _can_edit_lesson(self, lesson):
        return self.request.user.is_authenticated and lesson.module.course.owner_id == self.request.user.id

    def create(self, request, *args, **kwargs):
        module = get_object_or_404(Module, id=request.data.get("module"))
        if module.course.owner_id != request.user.id:
            return Response({"detail": "Only course owner can add lessons."}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_lesson(instance):
            return Response({"detail": "Only course owner can edit lessons."}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_lesson(instance):
            return Response({"detail": "Only course owner can edit lessons."}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_edit_lesson(instance):
            return Response({"detail": "Only course owner can delete lessons."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="test-code")
    def test_code(self, request, pk=None):
        lesson = self.get_object()
        code = request.data.get("code", "")
        run = run_python_code(code)

        status_value = Submission.Status.TESTED if run["ok"] else Submission.Status.ERROR
        submission = Submission.objects.create(
            user=request.user,
            lesson=lesson,
            code=code,
            output=run["output"],
            status=status_value,
        )

        return Response(
            {
                "submission_id": submission.id,
                "mode": "test",
                "ok": run["ok"],
                "status": submission.status,
                "output": run["output"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="submit-code")
    def submit_code(self, request, pk=None):
        lesson = self.get_object()
        code = request.data.get("code", "")
        run = run_python_code(code)

        if not run["ok"]:
            status_value = Submission.Status.ERROR
            is_correct = False
        else:
            is_correct = run["output"].strip() == lesson.expected_output.strip()
            status_value = Submission.Status.CORRECT if is_correct else Submission.Status.WRONG

        submission = Submission.objects.create(
            user=request.user,
            lesson=lesson,
            code=code,
            output=run["output"],
            status=status_value,
        )

        return Response(
            {
                "submission_id": submission.id,
                "mode": "submit",
                "status": submission.status,
                "is_correct": is_correct,
                "output": run["output"],
            },
            status=status.HTTP_200_OK,
        )


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related("lesson", "lesson__module")
