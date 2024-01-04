from django.db import models
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save, pre_delete
from editorjs_field.fields import EditorJSField
from .utils import unique_slug_generator
from users.models import NewUser as User
from django.contrib.postgres.fields import ArrayField
# Create your models here.


# POLITICIS = 'POLITICIS'
# BUSINESS = 'BUSINESS'
# HEALTH = 'HEALTH'
# ENTERTAINMENT = 'ENTERTAINMENT'
# SPORTS = 'SPORTS'
# STYLE = 'STYLE'
# SCIENCE = 'SCIENCE'
# TECHNOLOGY = 'TECHNOLOGY'
# TRAVEL = 'TRAVEL'
# WEATHER = 'WEATHER'
# EDUCATION = 'EDUCATION'
# POST_CATAGORY = [
#     (POLITICIS, 'Politics'),
#     (BUSINESS, 'Business'),
#     (HEALTH, 'Health'),
#     (SPORTS, 'Sports'),
#     (ENTERTAINMENT, 'Entertainment'),
#     (SCIENCE, 'Science'),
#     (STYLE, 'Style'),
#     (TECHNOLOGY, 'Technology'),
#     (TRAVEL, 'Travel'),
#     (WEATHER, 'Weather'),
#     (EDUCATION, 'Education'),
# ]


# class PostCategory(models.Model):
#     category = models.CharField(
#         max_length=30, choices=POST_CATAGORY, default=POLITICIS)

#     def __str__(self):
#         return self.category


class Posts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    meta = models.CharField(max_length=200)
    description = EditorJSField()
    slug = models.SlugField(blank=True, unique=True, max_length=255)
    have_image = models.BooleanField(default=False)
    # category = ArrayField(models.CharField(
    #     max_length=20, default="Politics"), null=True, blank=True)
    # suspended = models.BooleanField(default=False)
    # is_primary = models.BooleanField(default=False)
    # is_secondary = models.BooleanField(default=False)
    # read_min = models.IntegerField(default=2)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # def get_category(self):
    #     return "\n".join([p.category for p in self.category.all()])


def post_pre_save_reciever(sender, instance, *args, **kwargs):
    print("slug", instance.slug)
    if not instance.slug or instance.slug == "":
        instance.slug = unique_slug_generator(instance)


pre_save.connect(post_pre_save_reciever, sender=Posts)


class Draft(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    meta = models.CharField(max_length=200, null=True, blank=True)
    description = EditorJSField()
    slug = models.SlugField(blank=True, unique=True, max_length=255)
    category = ArrayField(models.CharField(
        max_length=20, default="Politics"), null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.slug


def draft_pre_save_reciever(sender, instance, *args, **kwargs):
    print("slug", instance.slug)
    if not instance.slug or instance.slug == "":
        instance.slug = unique_slug_generator(instance)


pre_save.connect(draft_pre_save_reciever, sender=Draft)


class DraftPosts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    meta = models.CharField(max_length=200, null=True, blank=True)
    description = EditorJSField()
    slug = models.SlugField(blank=True, unique=True, max_length=255)
    category = ArrayField(models.CharField(
        max_length=200, default="Politics"), null=True, blank=True)
    read_min = models.IntegerField(default=2)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.slug


def draft_pre_save_reciever(sender, instance, *args, **kwargs):
    print("slug", instance.slug)
    if not instance.slug or instance.slug == "":
        instance.slug = unique_slug_generator(instance)


pre_save.connect(draft_pre_save_reciever, sender=DraftPosts)


class SuspendedPost(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    # date = models.DateTimeField(auto_now_add=True, null=True)
    # updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.post.title)


def suspended_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called")
    if obj := SuspendedPost.objects.filter(post=instance.post):
        obj.delete()


class IsPrimary(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    # date = models.DateTimeField(auto_now_add=True, null=True)
    # updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.post.title)


def primary_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called")
    if obj := IsPrimary.objects.all():
        obj.delete()


pre_save.connect(primary_pre_save_reciever, sender=IsPrimary)


class IsSecondary(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    # date = models.DateTimeField(auto_now_add=True, null=True)
    # updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.post.title)


def secondary_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called")
    if obj := IsSecondary.objects.filter(post=instance.post):
        obj.delete()


pre_save.connect(secondary_pre_save_reciever, sender=IsSecondary)


class TrendingPosts(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    # date = models.DateTimeField(auto_now_add=True, null=True)
    # updated = models.DateTimeField(auto_now=True, null=True)
    # date = models.DateTimeField(auto_now_add=True)
    # update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title


def trending_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called")
    if obj := TrendingPosts.objects.filter(post=instance.post):
        obj.delete()


pre_save.connect(trending_pre_save_reciever, sender=TrendingPosts)


class CategoryPosts(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    category = ArrayField(models.CharField(
        max_length=200, default="Politics"), null=True, blank=True)
    # date = models.DateTimeField(auto_now_add=True, null=True)
    # updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.post.slug


def categoryPosts_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called category")
    if obj := CategoryPosts.objects.filter(post=instance.post):
        obj.delete()


pre_save.connect(categoryPosts_pre_save_reciever, sender=CategoryPosts)


class ReadMinutesOfPosts(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    read_min = models.IntegerField(default=2)

    def __str__(self):
        return self.post.title


def readMinutesOfPosts_pre_save_reciever(sender, instance, *args, **kwargs):
    print("pre save called")
    if obj := ReadMinutesOfPosts.objects.filter(post=instance.post):
        obj.delete()


pre_save.connect(readMinutesOfPosts_pre_save_reciever,
                 sender=ReadMinutesOfPosts)
