import datetime

from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import *
import json


from shiristory.story_service.models import Group, StoryObject


def get_msg(message, status):
    return {'message': f'{status} {message}'}, status

# for now not specific to user
# TODO: pagination
def get_group_list(request):
    res_data = {}
    res_status = 200

    if request.method == 'GET':
        res_data = []

        groups_query = Group.objects.all()

        for group_item in groups_query:
            res_data.append({
                'group_id': str(group_item.group_id),
                'group_name': group_item.group_name
            })

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status, safe=False)

@csrf_exempt
def create_group(request):
    res_data = {}
    res_status = 200

    if request.method == 'POST':
        try:
            request_body = request.body
            req_body_json = json.loads(request.body)

            # check if the group already exists
            existing_groups = Group.objects.filter(group_name=req_body_json['group_name'])
            if existing_groups.exists():
                raise Exception("Group already exists!")

            # TODO: set the admin to the user who sent this request

            new_id = ObjectId()

            new_group = Group(
                group_id=new_id,
                group_name=req_body_json['group_name'],
                group_members=req_body_json['group_members'],
                group_admins=req_body_json['group_admins'],
                vote_duration=datetime.timedelta(seconds=req_body_json['vote_duration']),
                vote_threshold=req_body_json['vote_threshold'],
                stories=[ {
                    'story_id' : ObjectId(),
                    'user_id' : req_body_json['group_admins'][0],
                    'story_type': req_body_json['first_story']['story_type'],
                    'story_content': req_body_json['first_story']['story_content'],
                    'next_story_type': req_body_json['first_story']['next_story_type'],
                    'datetime': datetime.datetime.now(),
                    'vote_count': 0
                } ]
            )

            new_group.save()

            res_data = {
                'group_id': str(new_id)
            }

        except Exception as e:
            res_data, res_status = get_msg(f'{e}', 400)
    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status)

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
            res_data, res_status = get_msg("group not found", 404)

    else:
        res_data, res_status = get_msg('invalid request method', 405)

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
            res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)
        
        except ObjectDoesNotExist as e:
            res_data, res_status = get_msg(f"{e}", 404)

        except Exception as e:
            res_data, res_status = get_msg(f"{e}", 400)

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status)

@csrf_exempt
def edit_member(request, group_id):

    res_data = {}
    res_status = 200

    try:
        if request.method == 'POST':

            query_res = Group.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            if req_body_json['member_id'] in query_res.group_members:
                raise Exception("member already present!")

            query_res.group_members.append(req_body_json['member_id'])
            query_res.save()

            res_data, res_status = get_msg(f"member add ok", 200)

        elif request.method == 'DELETE':
            query_res = Group.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            if req_body_json['member_id'] not in query_res.group_members:
                raise Exception("member is not in group!")

            query_res.group_members.remove(req_body_json['member_id'])

            if req_body_json['member_id'] in query_res.group_admins:
                query_res.group_admins.remove(req_body_json['member_id'])

            query_res.save()

            res_data, res_status = get_msg(f"member delete ok", 200)

        else:
            res_data, res_status = get_msg('invalid request method', 405)

    except KeyError as e:
        res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

    except ObjectDoesNotExist as e:
        res_data, res_status = get_msg(f"group not found", 404)

    except Exception as e:
        res_data, res_status = get_msg(f"{e}", 400)


    return JsonResponse(res_data, status=res_status)

@csrf_exempt
def edit_admin(request, group_id):
    res_data = {}
    res_status = 200

    try:
        if request.method == 'POST':

            query_res = Group.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            if req_body_json['member_id'] not in query_res.group_members:
                raise Exception("member is not part of this group!")

            if req_body_json['member_id'] in query_res.group_admins:
                raise Exception("admin already present!")

            query_res.group_admins.append(req_body_json['member_id'])
            query_res.save()

            res_data, res_status = get_msg(f"admin add ok", 200)

        elif request.method == 'DELETE':
            query_res = Group.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            if req_body_json['member_id'] not in query_res.group_admins:
                raise Exception(f"member {req_body_json['member_id']} is not admin!")

            query_res.group_admins.remove(req_body_json['member_id'])
            query_res.save()

            res_data, res_status = get_msg(f"admin delete ok", 200)

        else:
            res_data, res_status = get_msg('invalid request method', 405)

    except KeyError as e:
        res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

    except ObjectDoesNotExist as e:
        res_data, res_status = get_msg(f"group not found", 404)

    except Exception as e:
        res_data, res_status = get_msg(f"{e}", 400)

    return JsonResponse(res_data, status=res_status)


