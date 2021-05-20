from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .models import Profile
from django.views.decorators.csrf import csrf_exempt
# TODO solve pip install not reflecting to IDE issue
# from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
import json

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({"message": "400 Unsupported HTTP method for this route"}, status=400)

    json_data = json.loads(request.body)
    try:
        username = json_data['username']
        password = json_data['password']
    except KeyError:
        return JsonResponse({"message": "400 Missing login fields"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({"message": "200 login OK"})

    return JsonResponse({"message": "401 mismatched login credentials " + username + " " + password},status=401)

@csrf_exempt
def signup_view(request):
    if request.method != 'POST':
        return JsonResponse({"message": "400 Unsupported HTTP method for this route"}, status=400)

    json_data = json.loads(request.body)

    try:
        username = json_data['username']
        password = json_data['password']
        email = json_data['email']
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

        # TODO Log user in by sending back a JWT token
        return JsonResponse({"message": "200 Signup OK"})

def testLoginView(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": "Logged In as " + request.user.username})
    return JsonResponse({"message": "NOT Logged In"})