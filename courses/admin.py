from django.contrib import admin
from .models import Course, CoursePart, Lesson, Enrollment, Review

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CoursePartInline(admin.TabularInline):
    model = CoursePart
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "teacher", "is_active", "created_at")
    inlines = [CoursePartInline]

@admin.register(CoursePart)
class CoursePartAdmin(admin.ModelAdmin):
    list_display = ("course", "name", "price_z", "num_videos", "num_texts")
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "part", "lesson_type", "order")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "part", "created_at", "is_trial", "progress_percent")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "rating", "created_at")
