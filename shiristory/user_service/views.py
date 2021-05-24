from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import environ

# JWT imports
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from shiristory.user_service.models import User

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


@api_view(['POST'])
@permission_classes(())
@authentication_classes(())
@csrf_exempt
def login_view(request):
    # We are adding extra message to the response of simplejwt token generating view
    res = (TokenObtainPairView.as_view()(request._request))
    status_code = res.status_code
    if status_code == 200:
        res.data["message"] = "200 Login OK"
    else:
        res.data["message"] = str(status_code) + " Login Failed"

    return res

# TODO Replace to Global variable
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()
domain = env('DOMAIN')


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
    profile_pic_url = domain + '/media/sample.jpg'

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

@api_view(['GET'])
def me_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": "Logged In as " + request.user.username})
    return JsonResponse({"message": "NOT Logged In"})


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
            "user": {
                "id": str(logged_in_user.pk),
                "nickname": logged_in_user.nickname,
                "bio": logged_in_user.bio,
                "profile_pic_url": logged_in_user.profile_pic_url
            }
        })

    # POST request
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