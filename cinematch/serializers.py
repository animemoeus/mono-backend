from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Genre, Movie, Talent


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
        ]


class TalentSerializer(ModelSerializer):
    class Meta:
        model = Talent
        fields = [
            "id",
            "name",
        ]


class MovieListSerializer(ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    talent = TalentSerializer(many=True, read_only=True)
    similarity_score = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "release_date",
            "rating",
            "genre",
            "talent",
            "original_language",
            "similarity_score",
            "created_at",
            "updated_at",
        ]
