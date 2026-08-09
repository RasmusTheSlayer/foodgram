from rest_framework.pagination import PageNumberPagination

LIMIT_QUERY_PARAM = 'limit'


class RecipePagination(PageNumberPagination):
    page_size_query_param = LIMIT_QUERY_PARAM
