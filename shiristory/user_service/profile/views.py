from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Profile
import json

# JWT imports
from rest_framework.decorators import api_view, permission_classes, authentication_classes


@api_view(['GET'])
def index(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse({
        "message": "200 get profile details OK",
        "user": {
            "id": profile.user_id,
            "nickname": profile.nickname,
            "bio": profile.bio,
            "profile_pic_url": profile.profile_pic_url
        }
    })


@api_view(['PUT'])
def nickname_update_view(request):
    json_data = json.loads(request.body)
    try:
        new_nickname = json_data['new_nickname']

    except KeyError:
        return JsonResponse({"message": "400 Missing nickname field"}, status=400)

    profile = Profile.objects.get(user=request.user)
    profile.nickname = new_nickname
    profile.save()

    return JsonResponse({"message": "200 Update nickname OK"})


@api_view(['PUT'])
def bio_update_view(request):
    json_data = json.loads(request.body)
    try:
        new_bio = json_data['new_bio']

    except KeyError:
        return JsonResponse({"message": "400 Missing bio field"}, status=400)

    profile = Profile.objects.get(user=request.user)
    profile.bio = new_bio
    profile.save(update_fields=['bio'])

    return JsonResponse({"message": "200 Update bio OK"})


@api_view(['PUT'])
def image_update_view(request):
    return HttpResponse("image_update_view")
