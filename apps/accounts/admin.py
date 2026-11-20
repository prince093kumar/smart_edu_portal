from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, StudentProfile, TeacherProfile

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False

@admin.action(description="Verify selected teachers (grant course creation)")
def verify_selected_teachers(modeladmin, request, queryset):
    count = 0
    for user in queryset.filter(role=User.Role.TEACHER):
        if hasattr(user, 'teacher_profile'):
            user.teacher_profile.is_verified = True
            user.teacher_profile.verified_at = timezone.now()
            user.teacher_profile.save()
            count += 1
    modeladmin.message_user(request, f"{count} teacher(s) successfully verified.")

@admin.action(description="Revoke verification for selected teachers")
def unverify_selected_teachers(modeladmin, request, queryset):
    count = 0
    for user in queryset.filter(role=User.Role.TEACHER):
        if hasattr(user, 'teacher_profile'):
            user.teacher_profile.is_verified = False
            user.teacher_profile.save()
            count += 1
    modeladmin.message_user(request, f"{count} teacher(s) marked unverified.")

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_teacher_verified_display', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    actions = [verify_selected_teachers, unverify_selected_teachers]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Smart Education Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Smart Education Role', {'fields': ('role',)}),
    )

    def is_teacher_verified_display(self, obj):
        if obj.role == User.Role.TEACHER:
            return getattr(getattr(obj, 'teacher_profile', None), 'is_verified', False)
        return "-"
    is_teacher_verified_display.boolean = True
    is_teacher_verified_display.short_description = "Verified Teacher"

    def get_inlines(self, request, obj=None):
        if obj and obj.role == 'student':
            return [StudentProfileInline]
        elif obj and obj.role == 'teacher':
            return [TeacherProfileInline]
        return []

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'class_name')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'qualification', 'is_verified', 'verified_at')
    list_filter = ('is_verified', 'department')
    actions = ['verify_profiles', 'unverify_profiles']

    @admin.action(description="Verify selected teacher profiles")
    def verify_profiles(self, request, queryset):
        queryset.update(is_verified=True, verified_at=timezone.now())

    @admin.action(description="Revoke verification for selected teacher profiles")
    def unverify_profiles(self, request, queryset):
        queryset.update(is_verified=False)
