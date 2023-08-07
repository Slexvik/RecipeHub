from rest_framework import status
from rest_framework.response import Response


class CreateDeleteMixin:

    def add_item(
            self,
            serializer_create_class,
            serializer_read_class,
            read_model,
            data,
            request,
            id,
    ):
        serializer = serializer_create_class(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        item = read_model.objects.get(id=id)
        serializer = serializer_read_class(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_item(self, model, **kwargs):
        instance = model.objects.filter(**kwargs)

        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'errors': 'Вы не подписаны на автора.'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
