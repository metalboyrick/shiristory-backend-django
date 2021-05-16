from django.http import HttpResponse, JsonResponse


def index(request):
    return HttpResponse("Hello, world. You're at the story index.")


def get_group_info(request, group_id):
    return JsonResponse({'current_group_id': group_id})
