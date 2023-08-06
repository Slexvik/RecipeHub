from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class CreateDeleteMixin:

    def add_item(self, serializer_class, data, request):
        serializer = serializer_class(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_item(self, model, **kwargs):
        instance = get_object_or_404(model, **kwargs)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, NotFound):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
