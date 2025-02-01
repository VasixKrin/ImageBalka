from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action

import redis
from django.conf import settings

from .utils import get_most_viewed_image

# redis connection
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            messages.success(request, 'Image added successfully.')
            create_action(request.user, 'has bookmarked a new image', new_image)
            # redirect to the new created item detail veiw
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {
            'section': 'images',
            'form': form
        }
    )


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Increment total image views by 1
    total_views = r.incr(f'image:{image.id}:views')
    # Increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images', 'image': image, 'total_views': total_views},
    )


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 4)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # if AJAX request and page out of range
            # return an empty page
            return HttpResponse('')
        # if page out of range return last page of results
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {'section': 'images', 'images': images}
        )
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images}
    )


@login_required
def image_ranking(request):
    most_viewed = get_most_viewed_image()
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed}
    )
