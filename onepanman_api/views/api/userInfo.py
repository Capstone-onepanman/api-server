from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from onepanman_api.models import UserInfo
from onepanman_api.permissions import IsAdminUser, IsLoggedInUserOrAdmin
from rest_framework import viewsets, status

from onepanman_api import models
from onepanman_api import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = models.UserInfo.objects.all()
    serializer_class = serializers.UserInfoSerializer

    #permission_classes = [IsLoggedInUserOrAdmin]

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            serializer.save()
            return Response(serializer.data)

        except Exception as e:
            print("UPDATE FAIL ERROR : {}".format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            instance.nickname = "삭제 유저"
            instance.isCodeOpen = False
            instance.group = None
            instance.profileImage = "삭제 유저"

            serializer.save()

            return Response(serializer.data)

        except Exception as e:
            print("DESTROY FAIL ERROR : {}".format(e))

            return Response(status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        models.UserInfo.objects.create(user=instance)

class MyUserInfoView(APIView):

    def get(self, request, version):

        queryset = UserInfo.objects.all().filter(user=request.user.pk)[0]

        serializer = serializers.UserInfoSerializer(queryset)

        return Response(serializer.data)
