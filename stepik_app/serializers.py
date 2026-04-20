from rest_framework import serializers

from .models import Course, CourseReview, LessonTest, Module, Submission


class LessonMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTest
        fields = "__all__"


class ModuleMiniSerializer(serializers.ModelSerializer):
    lessons = LessonMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    modules = ModuleMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "modules")


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner", "created_at")


class ModuleSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source="course", read_only=True)
    lessons = LessonMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = "__all__"
        read_only_fields = ("course_detail", "lessons")


class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class LessonTestSerializer(serializers.ModelSerializer):
    module_detail = ModuleMiniSerializer(source="module", read_only=True)

    class Meta:
        model = LessonTest
        fields = "__all__"
        read_only_fields = ("module_detail",)


class LessonTestWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTest
        fields = "__all__"


class SubmissionSerializer(serializers.ModelSerializer):
    lesson_detail = LessonTestSerializer(source="lesson", read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"
        read_only_fields = ("user", "output", "status", "created_at", "lesson_detail")


class CourseReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CourseReview
        fields = "__all__"
        read_only_fields = ("user", "created_at")

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be from 1 to 5.")
        return value


class CodeRunRequestSerializer(serializers.Serializer):
    code = serializers.CharField()
