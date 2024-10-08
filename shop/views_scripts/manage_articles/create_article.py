from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from shop.forms import ArticleForm
from shop.models import Article
from shop.views import is_admin


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.priority = Article.objects.count()
            new_article.save()
            return redirect('admin_tools', feature_name='manage_articles')  # Redirect to a URL where you list articles or a success page
        else:
            print(form.errors)
    else:
        form = ArticleForm()
    articles = Article.objects.all().order_by('priority')
    print(articles)
    return render(request, 'admin_tools/AT_manage_articles.html', {'feature_name': "manage_articles", 'form': form, "articles": articles})

def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'GET':
        # Serialize the article data for the edit form
        data = {
            'article_name': article.article_name,
            'article_content': article.article_content,
            'mini_article_name': article.mini_article_name,
            'mini_article_text': article.mini_article_text,
            'mini_article_photo': article.mini_article_photo.url
        }
        return JsonResponse(data)
    elif request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            # Save the form without committing to the database
            article = form.save(commit=False)
            # Set the article_content field explicitly
            article.article_content = request.POST.get('article_content')
            article.save()  # Now save the article to the database
            return JsonResponse({'success': True})
        else:
            print(form.errors.as_data())
            return JsonResponse({'errors': form.errors}, status=400)

@login_required
@user_passes_test(is_admin)
def delete_article(request, article_id):
    # Получаем объект баннера, чтобы иметь доступ к связанному файлу изображения
    article = Article.objects.filter(id=article_id).first()
    if article:
        # Удаление файла изображения
        if article.image:
            # Удаление файла, если он существует
            image_path = article.image.path
            if default_storage.exists(image_path):
                default_storage.delete(image_path)
        # Удаление объекта баннера
        article.delete()
        # Перенумерация приоритетов оставшихся баннеров
        banners = Article.objects.all().order_by('priority')
        for index, remaining_banner in enumerate(banners):
            remaining_banner.priority = index
            remaining_banner.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Banner not found'})

@login_required
@user_passes_test(is_admin)
def move_up_article(request, article_id):
    article = Article.objects.get(id=article_id)
    previous_article = Article.objects.filter(priority__lt=article.priority).order_by('-priority').first()
    if previous_article:
        article.priority, previous_article.priority = previous_article.priority, article.priority
        article.save()
        previous_article.save()
    return JsonResponse({'status': 'ok'})

@login_required
@user_passes_test(is_admin)
def move_down_article(request, article_id):
    article = Article.objects.get(id=article_id)
    next_article = Article.objects.filter(priority__gt=article.priority).order_by('priority').first()
    if next_article:
        article.priority, next_article.priority = next_article.priority, article.priority
        article.save()
        next_article.save()
    return JsonResponse({'status': 'ok'})