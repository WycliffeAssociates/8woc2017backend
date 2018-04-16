import pickle
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import TaskSerializer
from ..models import Task

import redis

redis_client = redis.StrictRedis(host='redis')


class TaskViewSet(viewsets.ViewSet):
    serializer_class = TaskSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def list(self, request):
        task_list = []

        keys = redis_client.keys('celery-task-meta*')

        if len(keys):
            tasks = redis_client.mget(keys)
            for task in tasks:
                data = pickle.loads(task.strip(), encoding='UTF8')
                data = self.get_defaults_from_data(data)
                task_obj = self.get_task_from_data(data)
                task_list.append(task_obj)

        sorted_list = sorted(task_list, key=lambda k: k.started, reverse=True)
        serializer = TaskSerializer(
            instance=sorted_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            task = redis_client.get('celery-task-meta-' + pk)
            data = pickle.loads(task.strip(), encoding='UTF8')

            data = self.get_defaults_from_data(data)
            task_obj = self.get_task_from_data(data)
        except (KeyError, TypeError, AttributeError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(instance=task_obj)
        return Response(serializer.data)

    @staticmethod
    def get_defaults_from_data(data):
        dic = {
            "task_id": None,
            "status": None,
            "result": {
                "name": None,
                "title": "",
                "message": "",
                "details": "",
                "current": 0,
                "total": 0,
                "started": None,
                "finished": None,
            },
        }
        if "task_id" in data:
            dic["task_id"] = data["task_id"]
        if "status" in data:
            dic["status"] = data["status"]
        if "result" in data:
            if "name" in data["result"]:
                dic["result"]["name"] = data["result"]["name"]
            if "title" in data["result"]:
                dic["result"]["title"] = data["result"]["title"]
            if "message" in data["result"]:
                dic["result"]["message"] = data["result"]["message"]
            if "details" in data["result"]:
                dic["result"]["details"] = data["result"]["details"]
            if "current" in data["result"]:
                dic["result"]["current"] = data["result"]["current"]
            if "total" in data["result"]:
                dic["result"]["total"] = data["result"]["total"]
            if "started" in data["result"]:
                dic["result"]["started"] = data["result"]["started"]
            if "finished" in data["result"]:
                dic["result"]["finished"] = data["result"]["finished"]
        return dic

    @staticmethod
    def get_task_from_data(data):
        task_obj = Task()
        task_obj.id = data["task_id"]
        task_obj.name = data["result"]["name"]
        task_obj.status = data["status"]
        task_obj.title = data["result"]["title"]
        task_obj.message = data["result"]["message"]
        task_obj.details = data["result"]["details"]
        task_obj.current = data["result"]["current"]
        task_obj.total = data["result"]["total"]
        task_obj.started = data["result"]["started"]
        task_obj.finished = data["result"]["finished"]
        task_obj.progress = 0

        if task_obj.status == u'SUCCESS':
            task_obj.progress = 100
        elif task_obj.status == u'FAILURE':
            task_obj.progress = 0
        elif task_obj.status == 'PROGRESS':
            if data["result"]["total"] > 0:
                task_obj.progress = int(data["result"]["current"] / data["result"]["total"] * 100)

        return task_obj
