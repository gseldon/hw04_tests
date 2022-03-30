from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User
from .forms import PostForm

POSTS_COUNT = 10
User = get_user_model()


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """
    Функция для отображения групп.
    Фильтр только опубликованых постов.
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_number = request.GET.get('page')
    paginator = Paginator(posts, POSTS_COUNT)
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': user,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_count = Post.objects.filter(author=author).count()

    context = {
        'post': post,
        'post_count': post_count,
        'author': author,
    }
    return render(request, template, context)


# Проверяем, авторизован ли пользователь
@login_required
def post_edit(request, post_id):
    # используем тот же шаблон, что и для создания поста
    template = 'posts/create_post.html'
    # получаем модель для редактирования по номеру поста
    post = get_object_or_404(Post, pk=post_id)
    # проверим, что редактировать будет автор поста
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    # создаем форму, с данными поста для редактирования
    # с проверкой запроса POST
    form = PostForm(request.POST or None, instance=post)
    # проверка формы
    if form.is_valid():
        # если проверка формы прошла, сохраняем
        # и делаем редирект на информацию о постах
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
    }
    return render(request, template, context)
