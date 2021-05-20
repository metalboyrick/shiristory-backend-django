# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from shiristory.base.toolkits import save_uploaded_medias
from shiristory.timeline_service.models import Post


def index(request):
    return HttpResponse("Hello, world. You're at the timeline index.")


@csrf_exempt
def create(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(status=405)

    content = request.POST.get('content', '')
    inv_link = request.POST.get('inv_link', '')

    post = Post()
    post.content = content
    post.inv_link = inv_link
    post.comments = []

    if len(request.FILES) != 0:
        try:
            media_type = request.POST.get('media_type', 'unknown type')
            media = save_uploaded_medias(request, 'timeline')
            media = media[0]
            post.media = media
            post.media_type = media_type
        except Exception as e:
            return HttpResponseBadRequest(str(e), status=400)

    post.save()

    return JsonResponse({'post_id': post.get_id(), 'message': 'Create post ok.'})
