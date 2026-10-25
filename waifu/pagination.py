from rest_framework.pagination import CursorPagination, PageNumberPagination


class WaifuListPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50
    page_size_query_param = "count"


class WaifuSimilarPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "count"
    ordering = ("-similarity_score", "-id")
