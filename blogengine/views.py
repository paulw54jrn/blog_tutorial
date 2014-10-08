from django.shortcuts import render
from django.views.generic import ListView
from blogengine.models import Post, Category, Tag
from django.contrib.syndication.views import Feed

class CategoryListView(ListView):

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            category = Category.objects.get(slug = slug)
            return Post.objects.filter(category=category)
        except Category.DoesNotExist:
            return Post.objects.none()



class TagListView(ListView):

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            tag = Tag.objects.get(slug=slug)
            return tag.post_set.all()
        except Tag.DoesNotExist:
            return Post.objects.none()

class PostsFeed(Feed):
    title = 'RSS feed - posts'
    link = 'feeds/posts/'
    description_template = 'RSS feed - blog posts'

    def items(self):
        return Post.objects.order_by('-pub_date')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

