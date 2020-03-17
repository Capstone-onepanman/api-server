import django_filters
from onepanman_api.serializers import UserInformationInProblemSerializer, CodeSerializer
from rest_framework import viewsets

from onepanman_api.models import Game, UserInformationInProblem, Code
from onepanman_api.serializers.game import GameSerializer
from onepanman_api.permissions import IsAdminUser, IsLoggedInUserOrAdmin, OnlyAdminUser
from rest_framework.response import Response

from onepanman_api.views.api.updateScore import update_totalTier, update_tier
from rest_framework.views import APIView

from django.db.models import Q


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('problem', 'challenger', 'opposite')

    #permission_classes = [OnlyAdminUser]

    def game_error(self, data):
        result = data["result"]

        queryset = UserInformationInProblem.objects.all()
        codeset = Code.objects.all()

        if result == "challenger_error":
            error_user = queryset.filter(user=data["challenger"])[0]
            normal_user = queryset.filter(user=data["opposite"])[0]
        else:
            error_user = queryset.filter(user=data["opposite"])[0]
            normal_user = queryset.filter(user=data["challenger"])[0]

        error_code = codeset.filter(author=error_user.user)[0]

        try:
            # update code to not available to game
            code_data = {
                "id": error_code.id,
                "author": error_user.pk,
                "language": error_code.language.id,
                "name": error_code.name,
                "available_game": False,
                "problem": error_user.problem.pk,
                "code": error_code.code,
            }

            code_serializer = CodeSerializer(data=code_data)
            code_serializer.is_valid(raise_exception=True)
            valid_code = code_serializer.validated_data

            error_code.available_game = valid_code["available_game"]
        except Exception as e:
            print("game_error - update code error : {}".format(e))

        try:
            # update error user's score
            error_score = error_user.score - 50

            error_user_data = {
                "id": error_user.id,
                "score": error_score,
                "user": error_user.pk,
                "available_game": False,
            }

            UIIPserializer = UserInformationInProblemSerializer(data=error_user_data)
            UIIPserializer.is_valid(raise_exception=True)
            valid_UIIP = UIIPserializer.validated_data

            error_user.score = valid_UIIP["score"]
            error_user.available_game = valid_UIIP["available_game"]

        except Exception as e:
            print("game_error - error user's score update error : {}".format(e))

        try:
            # update normal user's score
            normal_score = normal_user.score + 20

            normal_user_data = {
                "id": normal_user.id,
                "score": normal_score,
                "user": normal_user.pk,
                "code": normal_user.code.id,
            }

            UIIPserializer = UserInformationInProblemSerializer(data=normal_user_data)
            UIIPserializer.is_valid(raise_exception=True)
            valid_UIIP = UIIPserializer.validated_data

            normal_user.score = valid_UIIP["score"]
            normal_user.code = valid_UIIP["code"]
        except Exception as e:
            print("game_error - normal user's score error : {}".format(e))

        # save
        error_user.save()
        normal_user.save()
        error_code.save()

    def game_finish(self, data):
        winner = data["winner"]

        queryset = UserInformationInProblem.objects.all()

        challenger = queryset.filter(user=data["challenger"])[0]
        opposite = queryset.filter(user=data["opposite"])[0]

        # bonus score
        score_bonus = challenger.score - opposite.score

        if score_bonus < 0:
            score_bonus = -1*score_bonus

        if score_bonus > 20:
            score_bonus = 20

        # update score
        if winner == "challenger":
            if challenger.score < opposite.score:
                challenger_score = challenger.score + 20 + score_bonus
                opposite_score = opposite.score - 20 - score_bonus
            else :
                challenger_score = challenger.score + 20
                opposite_score = opposite.score - 20
        elif winner == "opposite":
            if challenger.score > opposite.score:
                challenger_score = challenger.score - 20 - score_bonus
                opposite_score = opposite.score + 20 + score_bonus
            else:
                challenger_score = challenger.score - 20
                opposite_score = opposite.score + 20
        elif winner == "draw":
            challenger_score = challenger.score
            opposite_score = opposite.score

        challenger_data = {
            "id": challenger.id,
            "user": challenger.user.pk,
            "score": challenger_score,
            "code": data["challenger_code"],
        }

        opposite_data = {
            "id": opposite.id,
            "user": opposite.user.pk,
            "score": opposite_score,
            "code": data["opposite_code"],
        }

        try:
            serializer = UserInformationInProblemSerializer(data=challenger_data)
            serializer.is_valid(raise_exception=True)
            challenger_data_validated = serializer.validated_data

            serializer = UserInformationInProblemSerializer(data=opposite_data)
            serializer.is_valid(raise_exception=True)
            opposite_data_validated = serializer.validated_data

            challenger.score = challenger_data_validated["score"]
            challenger.code = challenger_data_validated["code"]

            opposite.score = opposite_data_validated["score"]
            opposite.code = opposite_data_validated["code"]
        except Exception as e:
            print("game_finish - update user score & code error : {} ".format(e))

        challenger.save()
        opposite.save()

    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs)
        data = data.data
        result = data["result"]

        if result == "playing":
            return Response(data)

        if result == "challenger_error" or result == "opposite_error":
            self.game_error(data)

        if result == "finish":
            self.game_finish(data)

        update_tier(problemid=data["problem"])
        update_totalTier()

        return Response(data)

class MyGameView(APIView):

    def get(self, request, version):

        queryset = Game.objects.all().filter(Q(challenger=request.user.pk) | Q(opposite=request.user.pk))
        serializer = GameSerializer(queryset, many=True)

        return Response(serializer.data)