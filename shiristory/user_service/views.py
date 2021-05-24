import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# JWT imports
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from shiristory import settings
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
def profile_view(request):
    logged_in_user = request.user

    if request.method == 'GET':
        return JsonResponse({
            "message": "200 get profile details OK",
            "user": logged_in_user.to_dict(exclude=['password'])
        })

    # PUT request
    else:
        json_data = json.loads(request.body)
        try:
            new_nickname = json_data['new_nickname']
            new_bio = json_data['new_bio']

        except KeyError:
            return JsonResponse({"message": "400 Missing nickname field"}, status=400)

        logged_in_user.nickname = new_nickname
        logged_in_user.nickname = new_bio
        logged_in_user.save()

    return JsonResponse({"message": "200 Update profile info OK"})
