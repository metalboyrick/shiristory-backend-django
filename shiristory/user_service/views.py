import json

from bson import ObjectId
from bson.errors import InvalidId
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# JWT imports
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from shiristory import settings
from shiristory.base.toolkits import save_uploaded_medias
from shiristory.user_service.models import User


def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


@api_view(['POST'])
@permission_classes(())
@authentication_classes(())
@csrf_exempt
def signup_view(request):
    json_data = json.loads(request.body)
    try:
        username = json_data['username']
        password = json_data['password']
        email = json_data['email']

    except KeyError:
        return JsonResponse({"message": "400 Missing sign up fields"}, status=400)

    # Fill fields for a shiristory profile
    nickname = json_data['username']
    bio = "Default Bio"
    profile_pic_url = f'{settings.APP_URL}:{settings.APP_PORT}{settings.MEDIA_URL}sample.jpg'

    if User.objects.filter(username=username).exists():
        return JsonResponse({"message": "409 Signup user already exists"}, status=409)
    else:
        new_user = User(username=username,
                        email=email,
                        nickname=nickname,
                        bio=bio,
                        profile_pic_url=profile_pic_url
                        )
        new_user.set_password(password)
        new_user.save()

        return JsonResponse({"message": "Sign up OK"})


@api_view(['POST'])
@csrf_exempt
def reset_password_view(request):
    json_data = json.loads(request.body)
    try:
        new_password = json_data['new_password']
    except KeyError:
        return JsonResponse({"message": "400 Missing new password field"}, status=400)

    # TODO send email for verification

    # .get throws model.DoesNotExist exception if not found
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        user = None

    if user is None:
        return JsonResponse({"message": "404 User not found"})

    # update user password
    user.set_password(new_password)
    user.save()

    return JsonResponse({"message": "200 Reset password OK"})


@api_view(['GET', 'PUT'])
@csrf_exempt
def profile_view(request):
    logged_in_user = request.user

    if request.method == 'GET':
        return JsonResponse({
            "message": "200 get profile details OK",
            "user": logged_in_user.to_dict(exclude=['password'])
        })
    # PUT request
    else:

        logged_in_user.nickname = request.data.get("new_nickname", logged_in_user.nickname)
        logged_in_user.bio = request.data.get("new_bio", logged_in_user.bio)

        if len(request.FILES) != 0:
            try:
                media = save_uploaded_medias(request, 'user')
                url = media[0]
                logged_in_user.profile_pic_url = url

            except Exception as e:
                logged_in_user.save()
                return JsonResponse(str(e), status=400)

        logged_in_user.save()
        return JsonResponse({"message": "Update profile info OK"})

@api_view(['POST'])
def add_friend(request, friend_username):
    try:
        logged_in_user = request.user
        friends = logged_in_user.friends
        friends_list = list(friends.get_queryset())
        new_friend = User.objects.get(username=friend_username)

        if new_friend not in friends_list:
            friends.add(new_friend)
            return JsonResponse({"message": "Add friend OK"})

        return JsonResponse({"message": "Friend exists!"})

    except User.DoesNotExist:
        return JsonResponse({"message": "User does not exist"})

    except InvalidId:
        return JsonResponse({"message": "Invalid Id"})

@api_view(['GET'])
def search_friend(request, query):
    try:
        logged_in_user = request.user
        friends = logged_in_user.friends
        friends_list = list(friends.get_queryset())

        matched = []
        for friend in friends_list:
            if query in friend.nickname:
                matched.append(friend.to_dict(exclude=['password']))
        return JsonResponse({
            "message": "Search friend OK",
            "candidates": matched
        })
    except User.DoesNotExist:
        return JsonResponse({"message": "User does not exist"})

    except InvalidId:
        return JsonResponse({"message": "Invalid Id"})

@api_view(['DELETE'])
def delete_friend(request, friend_id):
    try:
        logged_in_user = request.user
        friends = logged_in_user.friends
        friends_list = list(friends.get_queryset())

        if friend_id not in [str(friend._id) for friend in friends_list]:
            return JsonResponse({"message": "Friend does not exist"})

        friends.remove(User.objects.get(pk=ObjectId(friend_id)))

        return JsonResponse({"message": "Delete friend OK"})

    except User.DoesNotExist:
        return JsonResponse({"message": "User does not exist"})

    except InvalidId:
        return JsonResponse({"message": "Invalid Id"})

