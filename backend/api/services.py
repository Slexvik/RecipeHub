from django.db.models import F, Sum
from django.http import HttpResponse


def create_shopping_cart(user, items):
    shopping_cart = [
        f'Список покупок для:\n{user.first_name}\n\n'
    ]
    items = items.values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        name=F('ingredient__name'),
        units=F('ingredient__measurement_unit'),
        total=Sum('amount'),
    ).order_by('name')

    text = '\n'.join([
        f'{item["name"]} ({item["units"]}) - {item["total"]}'
        for item in items
    ])
    shopping_cart.extend(text)
    shopping_cart.append('\n\nРассчитано в Foodgram')
    filename = 'foodgram_shoping_cart.txt'
    response = HttpResponse(shopping_cart, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
