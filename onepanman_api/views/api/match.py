from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from onepanman_api.models import UserInformationInProblem, Code, ProblemRuleInfo, RuleInfo, Problem
import random
import requests


class GetCoreResponse(Response):

    def close(self):
        super().close()

        # testing
        url = "http://127.0.0.1:8000/api/v1/user/1"
        response = requests.get(url)
        res_status = response.status_code
        res_data = response.text
        print("status : {} , text : {} ".format(res_status, res_data))


class Match(APIView):

    def getRules(self, problemid, ruleType):
        queryset = ProblemRuleInfo.objects.all().filter(problem=problemid)

        ruleids = []
        for model_instance in queryset:
            ruleids.append(model_instance.rule.id)

        rules = RuleInfo.objects.all().filter(type=ruleType, id__in=ruleids)

        result = []
        for model_instance in rules:
            result.append(model_instance.id)

        return result

    def match(self, userid, problemid, codeid):

        queryset_up = UserInformationInProblem.objects.all().filter(problem=problemid).order_by('-score')
        challenger = queryset_up.filter(user=userid)

        queryset_up = queryset_up.exclude(user=userid)
        problems = Problem.objects.all().filter(id=problemid)
        problem = problems[0]

        high_scores = queryset_up.filter(score__gte=challenger[0].score).order_by('-score')
        low_scores  = queryset_up.filter(score__lte=challenger[0].score).order_by('-score')

        if len(queryset_up) < 6 : # 게임을 플레이한 사람이 6명 미만인 경우
            opposite_index = random.randint(0,len(queryset_up))

            opposite = queryset_up[opposite_index]

        elif len(challenger) == 0:  # challenger가 이 게임이 첫판인 경우
            middle = int(len(queryset_up) / 2)
            opposite_index = random.randint(-2, 3) + middle
            opposite = queryset_up[opposite_index]

        elif len(high_scores) < 3 :  # challenger가 top3인 경우 ( 위에 3명이 없는 경우 )
            opposite_list = high_scores[:]
            low_range = (3 + (3 - len(high_scores)))
            opposite_list += low_scores[:low_range]
            opposite_index = random.randint(0, 5)

            opposite = opposite_list[opposite_index]

        elif len(low_scores) < 3: # challenger가 최하위권인 경우 ( 아래에 3명이 없는 경우 )
            opposite_list = low_scores[:]
            high_range = len(high_scores) - (3 + (3 - len(low_scores)))
            opposite_list += high_scores[high_range:]
            opposite_index = random.randint(0, 5)
            #print("low length : {} , high length : {} , index : {} , list length : {} , high range : {}".format(len(low_scores), len(high_scores), opposite_index, len(opposite_list), high_range))
            opposite = opposite_list[opposite_index]

        else:
            opposite_list = high_scores[-3:] + low_scores[:3]
            opposite_index = random.randint(0,5)
            opposite = opposite_list[opposite_index]

        placement = self.getRules(problemid, "placement")
        action    = self.getRules(problemid, "action")
        ending    = self.getRules(problemid, "ending")

        matchInfo = {
            "challenger": userid,
            "opposite": opposite.user.pk,
            "challenger_code": codeid,
            "opposite_code": opposite.code.id,
            "problem": problemid,
            "placement": placement,
            "action": action,
            "ending": ending,
            "board_size": problem.board_size,
            "board_info": problem.board_shape,
        }

        #print(matchInfo)

        return matchInfo

    def get(self, request, version):
        try:
            data = request.data

            userid = data['userid']
            problemid = data['problemid']
            codeid = data['codeid']

            matchInfo = self.match(userid, problemid, codeid)

            return GetCoreResponse(matchInfo)

        except Exception as e :
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)









