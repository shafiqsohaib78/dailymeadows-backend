from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from articles.models import (
    Posts, DraftPosts, CategoryPosts, ReadMinutesOfPosts)
from users.models import NewUser as User
from django.shortcuts import get_object_or_404
import json
# from PIL import Image
from datetime import datetime, date as date1, timedelta


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'user', 'username', 'title', 'image', 'meta',
                  'description', 'likes', 'time', 'date', 'updated']

    def get_image(self, obj):
        gObj = Posts.objects.get(id=obj.id)
        image = firstImage(gObj.description)
        print(image)
        return image

    def get_username(self, obj):
        return obj.user.username

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")

    def get_updated(self, obj):
        return obj.updated.strftime("%b %d, %Y")


class PostNavSearchSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'user', 'username', 'name', 'title',
                  'image', 'meta', 'slug', 'date']

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_username(self, obj):
        return obj.user.username

    def get_name(self, obj):
        return f"{obj.user.name}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class PostGetSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'user', 'name', 'title',
                  'meta', 'description', 'slug','category', 'image', 'date', 'read_min']

    def get_image(self, obj):
        return firstImage(obj.description)

    def get_user(self, obj):
        return obj.user.unique_id

    def get_name(self, obj):
        return obj.user.name
    
    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return min.read_min
    
    def get_category(self, obj):
        category = CategoryPosts.objects.get(post__id=obj.id)
        return category.category

    def get_date(self, obj):
        # print(obj.date.strftime("%b %d, %Y"))
        return obj.date.strftime("%b %d, %Y")


def checkUrl(obj):
    print(obj)
    test1 = json.loads(obj)
    print("test-->", test1)
    image = next(
        (
            obj['data']['url']
            for obj in test1['blocks']
            if obj['type'] == "image"
        ),
        None,
    )
    print("test image-->", image)


def firstImage(obj):
    image = None
    # print("obj-->>",obj)
    try:
        test1 = json.loads(obj)
        # print("test-->",test1)
        for obj in test1['blocks']:
            if obj['type'] == "image":
                image = obj['data']['url']
                break
        return image or None
    except Exception:
        return None

    # print("test image-->",image)


class PostFrontSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'username', 'name', 'title', 'image',
                  'meta', 'slug', 'category', 'read_min', 'date']

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_username(self, obj):
        return obj.user.username

    def get_category(self, obj):
        category = CategoryPosts.objects.get(post__id=obj.id)
        return category.category

    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return f"{min.read_min}"

    def get_name(self, obj):
        return f"{obj.user.name}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class PostMainBottomSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        ordering = ['date']
        fields = ['id', 'user', 'username', 'name', 'title', 'description', 'image',
                  'meta', 'category', 'read_min', 'slug', 'date']

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_username(self, obj):
        return obj.user.username

    def get_name(self, obj):
        return f"{obj.user.name}"

    def get_category(self, obj):
        category = CategoryPosts.objects.get(post__id=obj.id)
        return category.category

    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return f"{min.read_min}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class PostSecondrySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'username', 'name', 'title',
                  'description', 'image', 'slug', 'category', 'read_min', 'date',]

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_username(self, obj):
        return obj.user.username

    def get_name(self, obj):
        return f"{obj.user.name}"

    def get_category(self, obj):
        category = CategoryPosts.objects.get(post__id=obj.id)
        return category.category

    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return f"{min.read_min}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class CategoryAllPostSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        ordering = ['-time']
        fields = ['id', 'user', 'title',
                  'image', 'meta', 'slug', 'read_min', 'date', 'time']

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_user(self, obj):
        return obj.user.unique_id

    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return f"{min.read_min}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class AccountAllPostSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    read_min = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        ordering = ['-time']
        fields = ['id', 'user', 'name', 'title',
                  'image', 'meta', 'slug', 'read_min', 'time', 'date']

    def get_image(self, obj):
        try:
            gObj = Posts.objects.get(id=obj.id)
            return firstImage(gObj.description)
        except Exception:
            return None

    def get_user(self, obj):
        return obj.user.unique_id

    def get_name(self, obj):
        return obj.user.name

    def get_read_min(self, obj):
        min = ReadMinutesOfPosts.objects.get(post__id=obj.id)
        return f"{min.read_min}"

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = '__all__'


class ArticleEditDetailSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'user', 'username', 'slug']

    def get_username(self, obj):
        return obj.user.username


class DraftPostsEditDetailSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = DraftPosts
        fields = ['id', 'user', 'username', 'slug']

    def get_username(self, obj):
        return obj.user.username


class DraftPostsGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = DraftPosts
        fields = ['id', 'user', 'title', 'meta', 'description','category','read_min', 'slug', 'date']


class DraftPostsAccGeneralSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = DraftPosts
        ordering = ['-time']
        fields = ['id', 'user', 'name', 'title', 'description',
                  'image', 'meta', 'slug', 'read_min', 'time', 'date']

    def get_image(self, obj):
        try:
            return firstImage(obj.description)
        except Exception:
            return None

    def get_user(self, obj):
        return obj.user.unique_id

    def get_name(self, obj):
        return obj.user.name

    def get_date(self, obj):
        return obj.date.strftime("%b %d, %Y")
