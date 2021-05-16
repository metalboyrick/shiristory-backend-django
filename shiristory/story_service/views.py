from bson import ObjectId
from django.http import HttpResponse, JsonResponse

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
