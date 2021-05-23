# Create your views here.
import json

from bson import ObjectId
from bson.errors import InvalidId
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from shiristory.base.toolkits import save_uploaded_medias
from shiristory.timeline_service.models import Post


def index(request):
    if request.method != 'GET':
        return HttpResponseBadRequest(status=405)

    page = request.GET.get('page', 1)
    page_size = request.GET.get('size', 10)

    posts = Post.objects.all().order_by('-updated_at')
    paginator = Paginator(posts, page_size, allow_empty_first_page=True)

    try:
        page_result = paginator.page(page)
    except (PageNotAnInteger, EmptyPage) as exp:
        page_result = paginator.page(paginator.num_pages)

    post_data = []
    post_list = list(page_result.object_list)
    for post in post_list:
        post_dict = post.to_dict()
        post_data.append(post_dict)

    url = request.build_absolute_uri("/timeline/view")

    next_page_url = None
    if page_result.has_next():
        next_page_url = f'{url}?page={page_result.next_page_number()}&size={page_size}'

    previous_page_url = None
    if page_result.has_previous():
        previous_page_url = f'{url}?page={page_result.previous_page_number()}&size={page_size}'

    response_data = {
        'page': page,
        'page_size': paginator.per_page,
        'total_pages': paginator.num_pages,
        'next': next_page_url,
        'previous': previous_page_url,
        'posts': post_data
    }

    return JsonResponse(response_data)


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

    return JsonResponse({'post_id': post.get_id(), 'message': 'Create post OK'})


@csrf_exempt
def add_comment(request, post_id):
    if request.method != 'POST':
        return HttpResponseBadRequest(status=405)

    data = json.loads(request.body)

    try:
        object_id = ObjectId(post_id)
        post = Post.objects.get(pk=object_id)
        post.comments.append({
            'comment': data['comment'],
            'author': 'admin',
            'created_at': timezone.now()
        })
        post.save()

    except InvalidId:
        return HttpResponseNotFound("post_id not found")

    except KeyError:
        return HttpResponseBadRequest('Comment must not be empty')

    response = {
        '_id': post_id,
        'message': 'Add comment OK'
    }

    return JsonResponse(response)
