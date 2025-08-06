from rest_framework.pagination import CursorPagination


class MovieRecommendationPagination(CursorPagination):
    page_size = 10
    max_page_size = 50
    page_size_query_param = "count"
    ordering = "-similarity_score"
