from rest_framework.pagination import PageNumberPagination


class ProductListPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "count"


class CategoryListPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 50
    page_size_query_param = "count"
