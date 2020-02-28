from django.contrib.auth.models import User
from onepanman_api.views.api.match import Match
from rest_framework import viewsets, status
import os

from onepanman_api.serializers.user import UserSerializer, UserFullInfoSerializer
from rest_framework.response import Response
from .userInfo import UserInfoViewSet


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserFullInfoViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFullInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        Match.match(6,3,12)

        return super().retrieve(request, *args, **kwargs)
