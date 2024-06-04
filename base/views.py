from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class BaseListView(generics.ListAPIView):
    pagination_class = PageNumberPagination

class SuccessStatus(generics.GenericAPIView):
    throttle_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        return Response({"message" : "Success"})