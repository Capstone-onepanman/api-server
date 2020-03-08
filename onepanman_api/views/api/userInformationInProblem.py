import json

import django_filters
from onepanman_api.permissions import IsAdminUser, IsLoggedInUserOrAdmin, UserReadOnly
from rest_framework import viewsets, status

from onepanman_api.models import UserInformationInProblem, UserInfo
from onepanman_api.serializers.userInformationInProblem import UserInformationInProblemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core import serializers


class UserInformationInProblemViewSet(viewsets.ModelViewSet):
    queryset = UserInformationInProblem.objects.all().order_by('problem', '-score')
    serializer_class = UserInformationInProblemSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('user', 'problem', 'tier', 'score')
    # ordering_fields = ('user', 'problem', 'score')
    # ordering = ('user',)

    permission_classes = [UserReadOnly]

    def update(self, request, *args, **kwargs):
        try:
            data = super().update(request, *args, **kwargs)
            self.update_tier(data.data["problem"])
            self.update_totalTier()

            result = self.queryset.filter(user=data.data["user"], problem=data.data["problem"])
            result_json = serializers.serialize('json', result)
            result_json = json.loads(result_json)[0]
            result_json = result_json["fields"]

            return Response(result_json, status=status.HTTP_200_OK)

        except Exception as e:
            print("UPDATE ERROR : {}".format(e))

            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 문제 별 유저의 티어를 업데이트하는 함수
    def update_tier(self, problemid):
        instance_all = self.queryset.filter(problem=problemid).order_by('-score')

        for instance in instance_all:
            print("instance : {}".format(instance))
            user_score = instance.score
            instances = instance_all.exclude(id=instance.id)

            length_all = len(instances)
            instance_high = instances.filter(score__gte=user_score)

            #print("나보다 높은 사람의 수 : {}".format(len(instance_high)))

            if len(instance_high) == 0:  # 1등
                instance.tier = "Challenger"

            elif len(instance_high) < length_all/10:   # 상위 10%
                instance.tier = "Diamond"

            elif len(instance_high) < (length_all/100)*35:    # 상위 35%
                instance.tier = "Platinum"

            elif len(instance_high) < (length_all/100)*60:    # 상위 65%
                instance.tier = "Gold"

            elif len(instance_high) < (length_all/100)*90:    # 상위 90%
                instance.tier = "Silver"

            else:       # 상위 100%
                instance.tier = "Bronze"

            instance.save()

    # 유저의 전체 티어를 업데이트하는 함수
    def update_totalTier(self):
        users = UserInfo.objects.all().order_by('-tier_score')

        for user in users:

            tiers = UserInformationInProblem.objects.all().filter(user=user.pk)

            # 각 티어 별로 점수를 매기고 합산!
            score = 0

            for instance in tiers:
                tier = instance.tier

                if tier == "Challenger":
                    score += 100
                elif tier == "Diamond":
                    score += 70
                elif tier == "Platinum":
                    score += 60
                elif tier == "Gold":
                    score += 40
                elif tier == "Silver":
                    score += 20
                elif tier == "Bronze":
                    score += 10

            user.tier_score = score
            user.save()

            others = users.exclude(user=user.pk)
            high_users = others.filter(tier_score__gte=user.tier_score)

            high_length = len(high_users)
            total_length = len(others)

            if high_length < 1:
                user.tier = "Challenger"
            elif high_length < total_length/10:
                user.tier = "Diamond"
            elif high_length < (total_length/100)*35:
                user.tier = "Platinum"
            elif high_length < (total_length/100)*65:
                user.tier = "Gold"
            elif high_length < (total_length/100)*90:
                user.tier = "Silver"
            else:
                user.tier = "Bronze"

            user.save()

    #각 기능 별 권한 설정
    # def get_permissions(self):
    #     permission_classes = []
    #
    #     if self.action == "create" or self.action == "destroy" \
    #             or self.action == "update" or self.action == "partial_update":
    #         permission_classes = [IsAdminUser]  # 관리자만
    #
    #     if self.action == "list" or self.action == "retrieve":
    #         permission_classes = [IsLoggedInUserOrAdmin]  # 유저 or 관리자
    #
    #     return [permission() for permission in permission_classes]

