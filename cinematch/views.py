from pgvector.django import CosineDistance
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView

from backend.utils.openai import get_embedding

from .models import Movie
from .pagination import MovieRecommendationPagination
from .serializers import MovieListSerializer


class MovieRecommendationAPIView(ListAPIView):
    """
    API endpoint to get movie recommendations using vector similarity search.
    """

    serializer_class = MovieListSerializer
    pagination_class = MovieRecommendationPagination

    def get_queryset(self):
        query = self.request.query_params.get("query")

        if not query:
            raise ValidationError("Query parameter is required")

        try:
            # Generate embedding for the search query
            query_embedding = get_embedding(query)

            # Find movies with similar embeddings using cosine distance
            similar_movies = (
                Movie.objects.filter(embedding__isnull=False)
                .annotate(similarity_score=1 - CosineDistance("embedding", query_embedding))
                .order_by("-similarity_score")
                .prefetch_related("genre", "talent")
            )

            return similar_movies

        except Exception as e:
            raise ValidationError(f"Failed to generate recommendations: {str(e)}")
