from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Course, Module, Lesson, Enrollment, LessonProgress

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.action(description="Approve selected courses for public release")
def approve_courses(modeladmin, request, queryset):
    count = queryset.update(
        is_approved=True,
        is_published=True,
        approved_by=request.user,
        approved_at=timezone.now()
    )
    modeladmin.message_user(request, f"{count} course(s) approved and published to public.")

@admin.action(description="Revoke approval for selected courses")
def unapprove_courses(modeladmin, request, queryset):
    count = queryset.update(is_approved=False)
    modeladmin.message_user(request, f"Approval revoked for {count} course(s).")

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'category', 'banner_preview', 'is_approved', 'is_published', 'created_on')
    list_filter = ('is_approved', 'is_published', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    actions = [approve_courses, unapprove_courses]
    inlines = [ModuleInline]

    def banner_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 36px; width: 64px; object-fit: cover; border-radius: 4px;" />', obj.thumbnail.url)
        return "-"
    banner_preview.short_description = 'Banner'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'completed_on')
