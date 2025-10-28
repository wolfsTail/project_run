from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def contacts_view(request):
    return Response(
        {
            'company_name': 'Рога и панцирь',
            'slogan': 'Бегаем или за кем-то или от кого-то',
            'contacts': 'NDA'
        }
    )