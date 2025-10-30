from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from django.conf import settings

from .models import Run
from .serializers import RunSerializer, UserSerializer

@api_view(['GET'])
def contacts_view(request):
    return Response(
        {
            'company_name': 'Рога и панцирь',
            'slogan': 'Бегаем или за кем-то или от кого-то',
            'contacts': 'NDA'
        }
    )

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = settings.AUTH_USER_MODEL.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset.exclude(is_superuser=True)
        type = self.request.query_params.get('type', None)
        if not type:
            return qs
        if type == 'coach':
            return qs.filter(is_staff=True)
        if type == 'athlete':
            return qs.filter(is_staff=False)
        return qs
