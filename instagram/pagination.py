from rest_framework.pagination import PageNumberPagination


class InstagramUserListPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50
    page_size_query_param = "count"


class InstagramUserFollowerPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "count"


class InstagramUserFollowingPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "count"


class InstagramUserHistoryPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 50
    page_size_query_param = "count"
