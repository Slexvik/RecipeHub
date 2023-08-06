from foodgram_backand.settings import PAGE_SIZE_PAGINATION
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'
