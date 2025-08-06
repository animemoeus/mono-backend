from django.db import models


class Genre(models.Model):
    """Model representing a genre."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Talent(models.Model):
    """Model representing a talent (actor/actress)."""

    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """Model representing a movie."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    genre = models.ManyToManyField(Genre, related_name="movies")
    talent = models.ManyToManyField(Talent, related_name="movies")
    original_language = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
