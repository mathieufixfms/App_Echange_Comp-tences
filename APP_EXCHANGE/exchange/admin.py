from django.contrib import admin

from .models import (
    Availability,
    Category,
    HelpRequest,
    Skill,
    UserSkill,
)


# =========================================================
# Categories
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


# =========================================================
# Skills
# =========================================================

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "description",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
    )

    ordering = (
        "category__name",
        "name",
    )


# =========================================================
# User Skills
# =========================================================

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "skill",
        "get_category",
        "created_at",
    )

    list_filter = (
        "skill__category",
        "skill",
        "user",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "skill__name",
        "skill__category__name",
    )

    ordering = (
        "user__username",
        "skill__name",
    )

    @admin.display(
        description="Catégorie",
        ordering="skill__category__name",
    )
    def get_category(self, obj):
        return obj.skill.category


# =========================================================
# Availabilities
# =========================================================

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "skill",
        "get_category",
        "date",
        "is_booked",
        "created_at",
    )

    list_filter = (
        "is_booked",
        "date",
        "skill__category",
        "skill",
        "user",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "skill__name",
        "skill__category__name",
    )

    ordering = (
        "date",
    )

    @admin.display(
        description="Catégorie",
        ordering="skill__category__name",
    )
    def get_category(self, obj):
        return obj.skill.category


# =========================================================
# Help Requests
# =========================================================

@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "requester",
        "skill",
        "get_category",
        "activity",
        "date",
        "helper",
        "availability",
        "is_assigned_display",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "date",
        "skill__category",
        "skill",
        "requester",
        "helper",
    )

    search_fields = (
        "requester__username",
        "requester__first_name",
        "requester__last_name",
        "requester__email",
        "helper__username",
        "helper__first_name",
        "helper__last_name",
        "helper__email",
        "skill__name",
        "skill__category__name",
        "activity",
    )

    ordering = (
        "date",
    )

    @admin.display(
        description="Catégorie",
        ordering="skill__category__name",
    )
    def get_category(self, obj):
        return obj.skill.category

    @admin.display(
        boolean=True,
        description="Attribuée",
    )
    def is_assigned_display(self, obj):
        return obj.helper is not None