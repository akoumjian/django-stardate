from django.conf.urls import patterns, url
from django.views import generic

from stardate.models import Blog, Post
from stardate.views import BlogPostListView


urlpatterns = patterns('',
    url(r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<post_slug>[-\w]+)/$',
        generic.DetailView.as_view(
            model=Post,
            context_object_name='post',
            slug_url_kwarg='post_slug'), name='post_detail_view'),
    url(r'^(?P<slug>[-\w]+)/$', BlogPostListView.as_view(), name='blog_list_view'),
    url(r'^$', generic.ListView.as_view(
        model=Blog,
        context_object_name='blog_list'), name='blogs-list-view'),
)
