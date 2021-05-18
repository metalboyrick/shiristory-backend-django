import datetime

from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import *
import json


from shiristory.story_service.models import Group


def get_error_msg(message, status):
    return {'message': f'{status} {message}'}, status


def index(request):
    return HttpResponse("Hello, world. You're at the story index.")


def get_group_info(request, group_id):
    res_data = {}
    res_status = 200
    if request.method == 'GET':
        try:
            query_res = Group.objects.get(pk=ObjectId(group_id))
            res_data['group_name'] = query_res.group_name
            res_data['group_members'] = query_res.group_members
            res_data['group_admins'] = query_res.group_admins
            res_data['date_created'] = query_res.date_created
            res_data['status'] = query_res.status
            res_data['vote_duration'] = query_res.vote_duration
            res_data['vote_threshold'] = query_res.vote_threshold
        except Exception as e:
            res_data, res_status = get_error_msg("group not found", 404)

    else:
        res_data, res_status = get_error_msg('invalid request', 400)

    return JsonResponse(res_data, status=res_status)


@csrf_exempt
def edit_group_info(request, group_id):
    res_data = {}
    res_status = 200

    if request.method == 'PATCH':
        try:
            query_res = Group.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            req_body_json = json.loads(request.body)

            # check for all the params
            if len(req_body_json['group_name']) == 0:
                raise Exception("Group name cannot be empty")

            if req_body_json['vote_threshold'] > len(query_res.group_members):
                raise Exception("Vote threshold cannot exceed group member amount")

            query_res.group_name = req_body_json['group_name']
            query_res.status = req_body_json['status']
            query_res.vote_duration = datetime.timedelta(seconds=req_body_json['vote_duration'])
            query_res.vote_threshold = req_body_json['vote_threshold']

            query_res.save()

            res_data['group_name'] = req_body_json['group_name']
            res_data['status'] = req_body_json['status']
            res_data['vote_duration'] = req_body_json['vote_duration']
            res_data['vote_threshold'] = req_body_json['vote_threshold']

        except KeyError as e:
            res_data, res_status = get_error_msg(f"invalid input: {e} is missing", 400)
        
        except ObjectDoesNotExist as e:
            res_data, res_status = get_error_msg(f"{e}", 404)

        except Exception as e:
            res_data, res_status = get_error_msg(f"{e}", 400)

    else:
        res_data, res_status = get_error_msg('invalid request', 400)

    return JsonResponse(res_data, status=res_status)

@csrf_exempt
def edit_member(request, group_id):
    print(group_id)
    return JsonResponse({'message': 'Request to edit_member'}, status=200)

@csrf_exempt
def edit_admin(request, group_id):
    print(group_id)
    return JsonResponse({'message': 'Request to edit_admin'}, status=200)