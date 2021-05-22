from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
import json

# JWT imports
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView

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

@api_view(['POST'])
@permission_classes(())
@authentication_classes(())
@csrf_exempt
def signup_view(request):
    json_data = json.loads(request.body)
    try:
        username = json_data['username']
        password = json_data['password']
        email = json_data['username']
    except KeyError:
        return JsonResponse({"message": "400 Missing sign up fields"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"message": "409 Signup user already exists"},status=409)
    else:
        new_user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password)
        new_profile = Profile(user=new_user)
        new_profile.save()

        return login_view(request._request)

@api_view(['GET'])
def whoami_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": "Logged In as " + request.user.username})
    return JsonResponse({"message": "NOT Logged In"})

@api_view(['POST'])
@csrf_exempt
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "NOT Logged In"})

    # blacklist refresh_token
    refresh_token = OutstandingToken.objects.filter(user=request.user).latest('id')
    blacklisted_token = BlacklistedToken(token=refresh_token)
    blacklisted_token.save()

    return JsonResponse({"message": "200 logout OK"})

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

    # log user out for security measure
    logout_view(request._request)

    return JsonResponse({"message": "200 Reset password OK"})