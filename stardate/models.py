from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from stardate.parser import parse_file


class DropboxCommon(models.Model):
    bytes = models.IntegerField(blank=True)
    icon = models.CharField(max_length=255)
    is_dir = models.BooleanField()
    modified = models.DateTimeField(blank=True, null=True)
    path = models.CharField(max_length=255)
    rev = models.CharField(max_length=255)
    revision = models.IntegerField(blank=True, null=True)
    root = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    thumb_exists = models.BooleanField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.path


class DropboxFolder(DropboxCommon):
    hash = models.CharField(max_length=255)
    folder = models.ForeignKey('self', blank=True, null=True)


class DropboxFile(DropboxCommon):
    client_mtime = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True)
    folder = models.ForeignKey(DropboxFolder, blank=True, null=True)
    mime_type = models.CharField(max_length=255)


class Blog(models.Model):
    authors = models.ManyToManyField(User, blank=True, null=True)
    dropbox_file = models.ForeignKey(DropboxFile)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Blog, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Blog, self).save(*args, **kwargs)
        # Parse the dropbox_file and save individual posts
        posts = parse_file(self.dropbox_file.content)
        for post in posts:
            for key, value in post.items():
                if key == 'publish':
                    post[key] = datetime.strptime(value, '%m/%d/%Y')
                elif key == 'stardate':
                    post[key] = int(value)
                else:
                    post[key] = value
            p, created = Post.objects.get_or_create(stardate=post.get('stardate'), blog_id=self.id)
            p.__dict__.update(**post)
            p.save()

    @models.permalink
    def get_absolute_url(self):
        return ('blog_list_view', (), {'slug': self.slug})


class PostManager(models.Manager):

    def published(self):
        return self.get_query_set().filter(publish__lte=datetime.now()).order_by('-publish')


class Post(models.Model):
    authors = models.ManyToManyField(User, blank=True, null=True)
    blog = models.ForeignKey(Blog)
    body = models.TextField(blank=True)
    objects = PostManager()
    publish = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField()
    stardate = models.IntegerField()
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    # On save, a post should parse the dropbox blog file
    # and update the post that was changed.
    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('post_detail_view', (), {
            'blog_slug': self.blog.slug,
            'year': self.publish.year,
            'day': self.publish.day,
            'month': self.publish.strftime('%b').lower(),
            'post_slug': self.slug})
