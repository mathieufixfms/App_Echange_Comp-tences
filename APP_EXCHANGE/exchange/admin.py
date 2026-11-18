from django.contrib import admin

from .models import (
    Availability,
    Category,
    HelpRequest,
    Skill,
    UserSkill,
)


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


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
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


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "skill",
        "created_at",
    )

    list_filter = (
        "skill__category",
        "skill",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "skill__name",
    )

    ordering = (
        "user__username",
        "skill__name",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "skill",
        "date",
        "is_booked",
    )

    list_filter = (
        "is_booked",
        "date",
        "skill__category",
        "skill",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "skill__name",
    )

    ordering = (
        "date",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "requester",
        "skill",
        "date",
        "helper",
        "is_assigned",
    )

    list_filter = (
        "date",
        "skill__category",
        "skill",
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
        "activity",
    )

    ordering = (
        "date",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(
        boolean=True,
        description="Attribuée",
    )
    def is_assigned(self, obj):
        return obj.helper is not None
