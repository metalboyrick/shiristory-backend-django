# Create your views here.
import json

from bson import ObjectId
from bson.errors import InvalidId
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shiristory.base.toolkits import save_uploaded_medias
from shiristory.timeline_service.models import Post
from shiristory.user_service.models import User


@api_view(['GET'])
def index(request):
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
        # Exclude user password
        post_dict = post.to_dict(exclude=['password', 'friends'])
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
@api_view(['POST'])
def create(request):
    content = request.POST.get('content', '')
    inv_link = request.POST.get('inv_link', '')

    post = Post()
    # post.author = request.user
    post.author = User.objects.get(username='soo')
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
@api_view(['POST'])
def add_comment(request, post_id):
    data = json.loads(request.body)
    # user = request.user
    user = User.objects.get(username='soo')

    try:
        object_id = ObjectId(post_id)
        post = Post.objects.get(pk=object_id)
        comment = {
            'comment': data['comment'],
            'author': {
                '_id': user.get_id(),
                'username': user.username,
                'nickname': user.nickname,
                'profile_pic_url': user.profile_pic_url
            },
            'created_at': timezone.now()
        }
        post.comments.append(comment)
        post.save()

    except InvalidId:
        return HttpResponseNotFound("post_id not found")

    except KeyError:
        return HttpResponseBadRequest('Comment must not be empty')

    # Add post_id for response
    comment['post_id'] = post_id
    
    return JsonResponse(comment)


@csrf_exempt
@api_view(['POST'])
def like_post(request, post_id):
    # user = request.user
    user = User.objects.get(username='soo')
    try:
        object_id = ObjectId(post_id)
        post = Post.objects.get(pk=object_id)
        likes = list(post.likes.get_queryset())
        num_of_likes = len(likes)
        if user not in likes:
            post.likes.add(user)
            num_of_likes += 1
            post.save()

    except InvalidId:
        return HttpResponseNotFound("post_id not found")

    return JsonResponse({'post_id': post_id, 'num_of_likes': num_of_likes, 'message': 'Like post OK'})


@csrf_exempt
@api_view(['POST'])
def dislike_post(request, post_id):
    # user = request.user
    user = User.objects.get(username='soo')
    try:
        object_id = ObjectId(post_id)
        post = Post.objects.get(pk=object_id)
        likes = list(post.likes.get_queryset())
        num_of_likes = len(likes)
        if user in likes:
            post.likes.remove(user)
            num_of_likes -= 1
            post.save()

    except InvalidId:
        return HttpResponseNotFound("post_id not found")

    return JsonResponse({'post_id': post_id, 'num_of_likes': num_of_likes, 'message': 'Dislike post OK'})
