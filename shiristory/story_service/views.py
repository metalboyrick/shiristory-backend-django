import datetime
import json

from bson import ObjectId
from django.core.exceptions import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shiristory.settings import DATETIME_FORMAT
from shiristory.story_service.models import StoryGroup
from shiristory.user_service.models import User


def get_msg(message, status):
    return {'message': f'{status} {message}'}, status


@api_view(['GET'])
def get_group_list(request):
    res_data = {}
    res_status = 200

    user = User.objects.get(pk=request.user.pk)

    if request.method == 'GET':

        current_page = request.GET.get('page', 1)
        page_size = request.GET.get('size', 3)

        groups_query = StoryGroup.objects.all().order_by('-last_modified')
        user_groups = []
        for group in groups_query:
            if user.to_dict() in group.to_dict()["group_members"]:
                user_groups.append(group)

        paginator = Paginator(user_groups, page_size)

        url = request.build_absolute_uri("/story")

        try:
            page_result = paginator.page(current_page)
        except (PageNotAnInteger, EmptyPage) as exp:
            page_result = paginator.page(paginator.num_pages)

        res_data['page'] = current_page
        res_data['page_size'] = paginator.per_page
        res_data['total_pages'] = paginator.num_pages
        res_data[
            'next'] = f'{url}?page={page_result.next_page_number()}&size={page_size}' if page_result.has_next() else None
        res_data[
            'previous'] = f'{url}?page={page_result.previous_page_number()}&size={page_size}' if page_result.has_previous() else None
        res_data['groups'] = []

        group_list = list(page_result.object_list)

        for group_item in group_list:
            res_data['groups'].append({
                'group_id': str(group_item.pk),
                'group_name': group_item.group_name
            })

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status, safe=False)


@api_view(['POST'])
def create_group(request):
    res_data = {}
    res_status = 200
    user = request.user

    if request.method == 'POST':
        try:
            request_body = request.body
            req_body_json = json.loads(request.body)

            new_group = StoryGroup()

            new_group.group_name = req_body_json['group_name']

            for member_id in req_body_json['group_members']:
                member = User.objects.get(pk=ObjectId(member_id))
                new_group.group_members.add(member)

            new_group.group_admins.add(user)

            new_group.vote_duration = datetime.timedelta(seconds=req_body_json['vote_duration'])
            new_group.vote_threshold = req_body_json['vote_threshold']
            new_group.stories = [{
                '_id': ObjectId(),
                'author': new_group.group_admins.get_queryset()[0],
                'story_type': req_body_json['first_story']['story_type'],
                'story_content': req_body_json['first_story']['story_content'],
                'next_story_type': req_body_json['first_story']['next_story_type'],
                'datetime': datetime.datetime.now(),
                'vote_count': 0
            }]

            new_group.save()

            res_data, res_status = get_msg("success", 200)

            res_data = {
                'group_id': new_group.get_id()
            }

        except KeyError as e:
            res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

        except Exception as e:
            res_data, res_status = get_msg(f'{e}', 400)
    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status)


@api_view(['GET'])
def get_group_info(request, group_id):
    res_data = {}
    res_status = 200
    user = User.objects.get(pk=request.user.pk)

    if request.method == 'GET':
        try:
            object_id = ObjectId(group_id)
            query_res = StoryGroup.objects.get(pk=object_id)

            if user.to_dict() not in query_res.to_dict()["group_members"]:
                raise PermissionError

            res_data['group_name'] = query_res.group_name
            res_data['group_members'] = [
                member.to_dict(fields=['_id', 'username', 'first_name', 'last_name', 'nickname', 'profile_pic_url']) for
                member in query_res.group_members.get_queryset()]
            res_data['group_admins'] = [
                admin.to_dict(fields=['_id', 'username', 'first_name', 'last_name', 'nickname', 'profile_pic_url']) for
                admin in query_res.group_admins.get_queryset()]
            res_data['date_created'] = query_res.date_created.strftime(DATETIME_FORMAT)
            res_data['status'] = query_res.status
            res_data['vote_duration'] = str(query_res.vote_duration)
            res_data['vote_threshold'] = query_res.vote_threshold
        except ObjectDoesNotExist as e:
            res_data, res_status = get_msg("group not found", 404)
        except PermissionError as e:
            res_data, res_status = get_msg("unauthorized access", 403)

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status)


@api_view(['GET'])
def get_stories(request, group_id):
    res_data = {}
    res_status = 200

    user = User.objects.get(pk=request.user.pk)

    if request.method == 'GET':
        try:

            current_page = request.GET.get('page', 1)
            page_size = request.GET.get('size', 3)

            query_res = StoryGroup.objects.get(pk=ObjectId(group_id))

            if user.to_dict() not in query_res.to_dict()["group_members"]:
                raise PermissionError

            paginator = Paginator(query_res.stories, page_size)

            url = request.build_absolute_uri(f"/{group_id}/stories")

            try:
                page_result = paginator.page(current_page)
            except (PageNotAnInteger, EmptyPage) as exp:
                page_result = paginator.page(paginator.num_pages)

            res_data['page'] = current_page
            res_data['page_size'] = paginator.per_page
            res_data['total_pages'] = paginator.num_pages
            res_data[
                'next'] = f'{url}?page={page_result.next_page_number()}&size={page_size}' if page_result.has_next() else None
            res_data[
                'previous'] = f'{url}?page={page_result.previous_page_number()}&size={page_size}' if page_result.has_previous() else None
            res_data['stories'] = []

            for entry in list(page_result.object_list):
                res_data['stories'].append(
                    {
                        'story_id': str(entry['_id']),
                        'author': entry['author'],
                        'story_type': entry['story_type'],
                        'story_content': entry['story_content'],
                        'next_story_type': entry['next_story_type'],
                        'datetime': entry['datetime'].strftime(DATETIME_FORMAT),
                        'vote_count': entry['vote_count']
                    }
                )

        except ObjectDoesNotExist as e:
            res_data, res_status = get_msg("group not found", 404)

        except PermissionError as e:
            res_data, res_status = get_msg("unauthorized access", 403)

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status, safe=False)


@api_view(['PATCH'])
def edit_group_info(request, group_id):
    res_data = {}
    res_status = 200

    user = User.objects.get(pk=request.user.pk)

    if request.method == 'PATCH':
        try:
            query_res = StoryGroup.objects.get(pk=ObjectId(group_id))

            if not query_res:
                raise ObjectDoesNotExist()

            dict_query = query_res.to_dict()

            if user.to_dict() not in dict_query["group_admins"]:
                raise PermissionError

            req_body_json = json.loads(request.body)

            # check for all the params
            if len(req_body_json['group_name']) == 0:
                raise Exception("StoryGroup name cannot be empty")

            group_members = query_res.group_members.all()

            if req_body_json['vote_threshold'] > len(group_members):
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

        except PermissionError as e:
            res_data, res_status = get_msg(f"user not admin", 403)

        except KeyError as e:
            res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

        except ObjectDoesNotExist as e:
            res_data, res_status = get_msg(f"{e}", 404)

        except Exception as e:
            res_data, res_status = get_msg(f"{e}", 400)

    else:
        res_data, res_status = get_msg('invalid request method', 405)

    return JsonResponse(res_data, status=res_status)


@api_view(['POST', 'DELETE'])
def edit_member(request, group_id):
    res_data = {}
    res_status = 200

    try:

        query_res = StoryGroup.objects.get(pk=ObjectId(group_id))

        user = User.objects.get(pk=request.user.pk)

        if not query_res:
            raise ObjectDoesNotExist()

        dict_query = query_res.to_dict()

        if user.to_dict() not in dict_query["group_members"]:
            raise PermissionError

        req_body_json = json.loads(request.body)

        if not req_body_json['member_id']:
            raise KeyError('member_id')

        if request.method == 'POST':

            members = query_res.group_members.all()
            selected_member = User.objects.get(pk=ObjectId(req_body_json['member_id']))

            if selected_member in members:
                raise Exception("member already present!")

            query_res.group_members.add(selected_member)
            query_res.save()

            res_data, res_status = get_msg(f"member add ok", 200)

        elif request.method == 'DELETE':

            members = query_res.group_members.all()
            admins = query_res.group_admins.all()
            selected_member = query_res.group_members.get(pk=ObjectId(req_body_json['member_id']))

            if selected_member not in members:
                raise Exception("member is not part of this group!")

            query_res.group_members.remove(selected_member)

            if selected_member in admins:
                query_res.group_admins.remove(selected_member)

            query_res.save()

            res_data, res_status = get_msg(f"member delete ok", 200)

        else:
            res_data, res_status = get_msg('invalid request method', 405)

    except PermissionError as e:
        res_data, res_status = get_msg(f"Unauthorized access", 403)

    except KeyError as e:
        res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

    except ObjectDoesNotExist as e:
        res_data, res_status = get_msg(f"member or group not found", 404)

    except Exception as e:
        res_data, res_status = get_msg(f"{e}", 400)

    return JsonResponse(res_data, status=res_status)


@api_view(['POST', 'DELETE'])
def edit_admin(request, group_id):
    res_data = {}
    res_status = 200

    try:

        query_res = StoryGroup.objects.get(pk=ObjectId(group_id))

        user = User.objects.get(pk=request.user.pk)

        if not query_res:
            raise ObjectDoesNotExist()

        dict_query = query_res.to_dict()

        if user.to_dict() not in dict_query["group_admins"]:
            raise PermissionError

        if request.method == 'POST':

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            members = query_res.group_members.all()
            admins = query_res.group_admins.all()
            selected_member = query_res.group_members.get(pk=ObjectId(req_body_json['member_id']))

            if selected_member not in members:
                raise Exception("member is not part of this group!")

            if selected_member in admins:
                raise Exception("admin already present!")

            query_res.group_admins.add(selected_member)
            query_res.save()

            res_data, res_status = get_msg(f"admin add ok", 200)

        elif request.method == 'DELETE':

            req_body_json = json.loads(request.body)

            if not req_body_json['member_id']:
                raise KeyError('member_id')

            members = query_res.group_members.all()
            admins = query_res.group_admins.all()
            selected_member = query_res.group_members.get(pk=ObjectId(req_body_json['member_id']))

            if selected_member not in admins:
                raise Exception(f"member {req_body_json['member_id']} is not admin!")

            query_res.group_admins.remove(selected_member)
            query_res.save()

            res_data, res_status = get_msg(f"admin delete ok", 200)

        else:
            res_data, res_status = get_msg('invalid request method', 405)

    except KeyError as e:
        res_data, res_status = get_msg(f"invalid input: {e} is missing", 400)

    except ObjectDoesNotExist as e:
        res_data, res_status = get_msg(f"member or group not found", 404)

    except Exception as e:
        res_data, res_status = get_msg(f"{e}", 400)

    except PermissionError as e:
        res_data, res_status = get_msg(f"user not admin", 403)

    return JsonResponse(res_data, status=res_status)
