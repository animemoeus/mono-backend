from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from .models import Genre, Movie, Talent


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Talent)
class TalentAdmin(ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Movie)
class MovieAdmin(ModelAdmin):
    autocomplete_fields = ("genre", "talent")
    list_display = (
        "title",
        "rating",
        "release_date",
        "original_language",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "description", "genre__name", "talent__name")
    readonly_fields = ("created_at", "updated_at")
    list_filter = (
        ["genre", AutocompleteSelectFilter],
        ["talent", AutocompleteSelectFilter],
        "rating",
        "release_date",
        "original_language",
    )
    ordering = ("-release_date",)

    fieldsets = (
        (
            "Movie Information",
            {
                "fields": (
                    "title",
                    "description",
                    "release_date",
                    "rating",
                    "original_language",
                )
            },
        ),
        (
            "Relationships",
            {"fields": ("genre", "talent")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at")},
        ),
    )
