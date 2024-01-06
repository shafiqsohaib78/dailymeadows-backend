from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import concurrent.futures
# from enum import unique
# from django.urls.base import reverse
# from django.utils.translation import deactivate
# from rest_framework.pagination import LimitOffsetPagination

# from numpy.lib.type_check import imag
# from .utils import CheckNudity
# from threading import Thread
# import re
# import numpy as np
# import io
# import PIL.Image as Image
# from users.api.serializers import UserTrendingListSerializer
from articles.models import (
    Posts, DraftPosts, IsPrimary, IsSecondary, SuspendedPost,
    ReadMinutesOfPosts, CategoryPosts)
from rest_framework import generics, permissions
# from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
# from django_filters import rest_framework as filters1
# from nudenet import NudeClassifier
# from rest_framework.status import (
#     HTTP_201_CREATED,
#     HTTP_400_BAD_REQUEST,
#     HTTP_404_NOT_FOUND
# )
# from django.conf import settings
# import cv2
# import csv
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json
import requests
from .serializers import (PostSerializer, PostGetSerializer,
                          PostNavSearchSerializer, AccountAllPostSerializer, PostFrontSerializer, PostSecondrySerializer,
                          PostMainBottomSerializer, CategoryAllPostSerializer,
                          ArticleEditDetailSerializer,
                          DraftPostsEditDetailSerializer,
                          DraftPostsGetSerializer, DraftPostsAccGeneralSerializer)
from .pagination import (StandardResultsSetPagination,
                         ArticlesStatsPagination, PostMainBottomPagination)
from users.models import (NewUser as User)
import random
from rest_framework.exceptions import ValidationError
from pympler import asizeof
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# from validate_email import validate_email
from datetime import datetime, timedelta
current_month = datetime.now().month
# classifier = NudeClassifier()


class PostListView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = []
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]


class PostSearchView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = []
    queryset = Posts.objects.all()
    serializer_class = PostNavSearchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search == "":
            return []
        try:
            sus_posts = SuspendedPost.objects.all().values_list('post', flat=True)
            posts = Posts.objects.filter(
                ~Q(id__in=sus_posts) |
                Q(title__icontains=search)
                | Q(meta__icontains=search)
                | Q(slug__icontains=search)
            )
            print(posts)
            return (
                posts
            )
        except Exception:
            return []


class PostAccountSearchView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = []
    queryset = Posts.objects.all()
    serializer_class = PostNavSearchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        user = self.request.query_params.get('user')
        search = self.request.query_params.get('search')
        if search == "":
            queryset = []
            return queryset
        try:
            queryset = Posts.objects.filter(Q(title__icontains=search) | Q(
                meta__icontains=search) | Q(slug__icontains=search))
            return queryset.filter(Q(user__username=user))
        except:
            return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # print(self.request.query_params.get('post'))
        context.update(
            {
                "user": self.request.query_params.get('user'),
            }
        )
        return context


class PostSingleGetView(generics.ListAPIView):
    serializer_class = PostGetSerializer
    queryset = Posts.objects.all()
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get_queryset(self):
        post = self.request.query_params.get('post')
        if not (test := Posts.objects.filter(slug=post).exists()):
            raise ValidationError("Post not found.")
        else:
            return Posts.objects.filter(slug=post)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "post": self.request.query_params.get('post'),
            }
        )
        return context


class PostFrontGetView(generics.ListAPIView):
    permission_classes = [AllowAny,]
    serializer_class = PostFrontSerializer
    queryset = Posts.objects.all()
    # authentication_classes = []

    def get_queryset(self):

        try:
            # today = datetime.now()
            # past = datetime.now()-timedelta(days=5)
            # print(datetime.now())
            # print(datetime.now()-timedelta(days=5))
            # print(past)
            s_posts = SuspendedPost.objects.all().values_list('post', flat=True)
            f_posts = IsPrimary.objects.all().values_list('post', flat=True)
            return Posts.objects.filter(~Q(id__in=s_posts), Q(id__in=f_posts))
        except Exception:
            return []


class PostSecondryGetView(generics.ListAPIView):
    serializer_class = PostSecondrySerializer
    queryset = Posts.objects.all()
    permission_classes = [AllowAny,]
    # authentication_classes = []

    def get_queryset(self):
        try:

            posts = SuspendedPost.objects.all().values_list('post', flat=True)
            s_posts = IsSecondary.objects.all().values_list('post', flat=True)
            return Posts.objects.filter(~Q(id__in=posts), Q(id__in=s_posts))
        except Exception:
            return []


class PostMainBottomGetView(generics.ListAPIView):
    serializer_class = PostMainBottomSerializer
    queryset = Posts.objects.all()
    pagination_class = PostMainBottomPagination
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get_queryset(self):
        user = self.request.query_params.get('user')
        # print("user-->", user)
        # print("Ruser-->", self.request.user)
        # if self.request.user.is_anonymous:
        #     print("empty user")
        try:
            sus_posts = SuspendedPost.objects.all().values_list('post', flat=True)
            p_posts = IsPrimary.objects.all().values_list('post', flat=True)
            s_posts = IsSecondary.objects.all().values_list('post', flat=True)
            return Posts.objects.filter(~Q(id__in=sus_posts), ~Q(id__in=s_posts), ~Q(id__in=p_posts))
        except Exception:
            return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # print(self.request.query_params.get('post'))
        context.update(
            {
                "user": self.request.query_params.get('user'),
            }
        )
        return context


# class PostSingleLikeInfoView(generics.ListAPIView):
#     serializer_class = PostGetLikeSerializer
#     queryset = Posts.objects.all()
#     permission_classes = []
#     # authentication_classes = []

#     def get_queryset(self):
#         post = self.request.query_params.get('post')
#         # print(post)
#         try:
#             queryset = Posts.objects.filter(slug=post)
#             return queryset
#         except:
#             return []

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         # print(self.request.query_params.get('post'))
#         context.update(
#             {
#                 "user": self.request.query_params.get('user'),
#             }
#         )
#         return context


# class PostLikeViewset(viewsets.ModelViewSet):
#     serializer_class = PostLikeSerializer
#     queryset = Follow.objects.all()
#     filter_backends = (filters1.DjangoFilterBackend,)
#     filter_fields = ("user", "post",)
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def get(self, request, *args, **kwargs):
#         # print("like createView get called")
#         try:
#             likes = Follow.objects.all()
#             serializer = PostLikeSerializer(likes)
#             return Response(serializer.data)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#     def create(self, request):
#         try:
#             serializer = PostLikeSerializer(data=request.data)
#             if serializer.is_valid():
#                 likes = serializer.create(request)
#                 if likes:
#                     return Response(status=status.HTTP_201_CREATED)
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             print(request.data)
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_204_NO_CONTENT)


# class PostBookMarkViewset(viewsets.ModelViewSet):
#     serializer_class = PostBookMarkSerializer
#     queryset = BookMark.objects.all()
#     filter_backends = (filters1.DjangoFilterBackend,)
#     filter_fields = ("user", "post",)
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         if request.user.is_active:
#             try:
#                 likes = BookMark.objects.all()
#                 serializer = PostBookMarkSerializer(likes)
#                 return Response(serializer.data)
#             except:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_400_BAD_REQUEST)


#     def create(self, request):
#         if request.user.is_active:
#             try:
#                 serializer = PostBookMarkSerializer(data=request.data)
#                 if serializer.is_valid():
#                     likes = serializer.create(request)
#                     if likes:
#                         return Response(status=status.HTTP_201_CREATED)
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#             except:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         if request.user.is_active:
#             try:
#                 instance = self.get_object()
#                 self.perform_destroy(instance)
#                 return Response(status=status.HTTP_200_OK)
#             except:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# class BookMarkListView(generics.ListAPIView):
#     # authentication_classes = []
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = PostBookMarkListSerializer
#     pagination_class = StandardResultsSetPagination
#     queryset = BookMark.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         if self.request.user.is_active:
#             try:
#                 queryset = BookMark.objects.filter(user=user).order_by("-date")
#                 return queryset
#             except:
#                 return []
#         return []


# class PostDetailView(APIView):
#     # authentication_classes = []
#     permission_classes = []

#     def post(self, request, *args, **kwargs):

#         slug = request.data.get('slug')
#         # print(slug)
#         queryset = Posts.objects.filter(slug=slug)
#         # print(queryset)
#         # print(self.request.query_params.get('user'))
#         data = PostSerializer(data=queryset, context={
#                               "request": request, 'user': self.request.query_params.get('user')}, many=True)
#         data.is_valid()
#         return Response(data.data, status=status.HTTP_200_OK)

    # def get_queryset(self):
    #     print(self.request.data)
    #     slug = self.request.query_params.get('slug')
    #     # print(slug)
    #     queryset = Posts.objects.filter(slug=slug)
    #     return queryset

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context.update(
    #         {
    #             "user": self.request.query_params.get('user'),
    #         }
    #     )
    #     return context


class CategoryPostsListView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    queryset = Posts.objects.all()
    serializer_class = CategoryAllPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        category = self.request.query_params.get('category')
        print("category", category)

        try:
            category1 = CategoryPosts.objects.filter(
                category__icontains=category).values_list('post', flat=True)
            posts = Posts.objects.filter(id__in=category1).order_by("-date")
            # print(posts)
            return posts
        except Exception:
            return []


class AccountPostsListView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    queryset = Posts.objects.all()
    serializer_class = AccountAllPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        user = self.request.query_params.get('user')
        print("user post list", user)
        # print(user1.id)
        test = get_object_or_404(User, unique_id=user)
        print(test)
        try:
            return Posts.objects.filter(user__unique_id=user).order_by("-date")
        except Exception:
            return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "user": self.request.query_params.get('user'),
            }
        )
        return context


# class DiscoverPostsGetView(generics.ListAPIView):
#     serializer_class = DiscoverGetSerializer
#     queryset = Posts.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#     # authentication_classes = []

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         user1 = get_object_or_404(User, username=user)
#         user1_profile = get_object_or_404(Profile, user__username=user)
#         try:
#             suspended = Posts.objects.filter(
#                 suspended=True).values_list('id', flat=True)
#             block = UserBlock.objects.filter(
#                 block=user1).values_list('user', flat=True)
#             # print(block)
#             block1 = UserBlock.objects.filter(
#                 user=user1).values_list('block', flat=True)
#             # print(block1)
#             block2 = Profile.objects.filter(
#                 deactivated=True).values_list('user', flat=True)
#             # print(block2)
#             mute = UserMute.objects.filter(
#                 user=user1).values_list('mute', flat=True)
#             # print(mute)
#             mute1 = ArticleMute.objects.filter(
#                 user__username=user).values_list('mute', flat=True)
#             # print(mute1)
#             follow = Follow1.objects.filter(follower=user1_profile).values_list(
#                 "following__user", flat=True)
#             # print(follow)
#             # print("followpost-->", Posts.objects.filter(Q(user__in=follow)).count())
#             # user_list=Posts.objects.filter(~Q(user__username=user) & Q(user__in=follow)).exclude(user__in=mute).exclude(user__in=block).exclude(user__in=block1).exclude(id__in=mute1).exclude(user__in=block2)
#             # random_profiles_id_list = random.sample(list(user_list), min(len(user_list), 1000))
#             queryset = Posts.objects.filter(Q(user__in=follow)).exclude(user__in=mute).exclude(
#                 user__in=block).exclude(user__in=block1).exclude(id__in=mute1).exclude(user__in=block2).exclude(id__in=suspended).order_by('-date')
#             return queryset
#         except:
#             return []

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         # print(self.request.query_params.get('post'))
#         context.update(
#             {
#                 "user": self.request.query_params.get('user'),
#             }
#         )
#         return context


# def NudityDetect(url):
#     try:
#         image_bytes = io.BytesIO(url)
#         image = Image.open(image_bytes)
#         # print("animated-->>", image.is_animated)
#         # print("image-->>", image.n_frames)
#         if image.format=="GIF" or image.format=="gif":
#             # print("gif",image.n_frames)
#             for i in range (image.n_frames):
#                 # print("image index",image(i))
#                 image.seek(i)
#                 # image.show()
#                 result=classifier.classify(np.array(image))
#                 # print("result-->>",result)
#                 if result[0].get('unsafe') > result[0].get('safe'):
#                     return False
#             return True
#         else:
#             result = classifier.classify(np.array(image))
#             print("result-->>", result)
#             if result[0].get('unsafe') > result[0].get('safe'):
#                 # raise ValidationError("Senstive image should not be uploaded.")
#                 return False
#             else:
#                 return True
#     except:
#         return False


# class ContactUsCreateView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes=[permissions.AllowAny]

#     def post(self, request, *args, **kwargs):
#         name = request.data.get('name', None)
#         email = request.data.get('email', None)
#         subject = request.data.get('subject', None)
#         message = request.data.get('message', None)
#         file = request.data.get('file', None)
#         # print(file)

#         if name is None or name=="" or email is None or email=="" or subject is None or subject=="" or message is None or message=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             try:
#                 is_valid = validate_email(email,verify=True)
#                 # print(is_valid)
#                 if is_valid==True:
#                     contact=ContactUs()
#                     contact.name=name
#                     contact.email=email
#                     contact.subject=subject
#                     contact.message=message
#                     if file is not None:
#                         contact.file=file
#                     contact.save()
#                     return Response(status=status.HTTP_201_CREATED)
#                 else:
#                     return Response({"error":"Email not exists."},status=status.HTTP_403_FORBIDDEN)
#             except:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)


class PostCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        # categories = ["politics", "business"]
        title = request.data.get('title', None)
        user = request.data.get('user', None)
        meta = request.data.get('meta', None)
        read_min = request.data.get('read_min', None)
        description = request.data.get('description', None)
        category = request.data.get('category', None)
        category1 = json.loads(category)
        slug = request.data.get('slug', None)
        print("category", category)
        test1 = json.loads(description)
        # category1 = category[0:-1].split(', ')
        # print("category array", category1)
        # print(title)
        # print(meta)
        # print(description)

        try:
            print("try 1")
            size = asizeof.asizeof(test1)/1024
            # print(size)
            if size >= 1000:
                return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)
            if title is None or meta is None or description is None:
                return Response({"message": "There should be title/meta/description of the post."}, status=status.HTTP_400_BAD_REQUEST)
            if user is not None:
                try:
                    # print("user", user)
                    # print("refresh", refresh['id'])
                    # print("try 2")
                    refresh = RefreshToken(user)
                    if refresh['id'] is not None:
                        # print("id not none")
                        user1 = User.objects.get(id=refresh['id'])
                        # print("user1->", user1)
                        test_image = firstImage(description)
                        categoryP = CategoryPosts()
                        read_minP = ReadMinutesOfPosts()
                        if slug is None:
                            post = Posts()

                            if user1.is_active:
                                # print("slug is None")
                                post.user = user1
                                post.title = title
                                post.meta = meta
                                post.description = description
                                if test_image is not None:
                                    post.have_image = True
                                post.save()

                                # print(post)

                                categoryP.post = post
                                categoryP.category = category1
                                categoryP.save()

                                print(categoryP)

                                read_minP.post = post
                                read_minP.read_min = read_min
                                read_minP.save()
                                print(read_minP)

                                return Response({"message": "Post Created"}, status=status.HTTP_200_OK)
                            return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if user1.is_active:
                                checkP = Posts.objects.get(
                                    user__id=refresh['id'], slug=slug)
                                print("checkP",checkP)
                                if checkP:
                                    checkP.user = user1
                                    checkP.title = title
                                    checkP.meta = meta
                                    checkP.description = description
                                    if test_image is not None:
                                        checkP.have_image = True
                                    print(checkP)
                                    checkP.save()

                                    # print("done")

                                    categoryP.post = checkP
                                    categoryP.category = category1
                                    categoryP.save()

                                    print(categoryP)

                                    read_minP.post = checkP
                                    read_minP.read_min = read_min
                                    read_minP.save()
                                    print(read_minP)
                                    return Response({"message": "Post Successfully Updated"}, status=status.HTTP_200_OK)
                            return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                            # prev_post=Posts.objects.filter(user__unique_id=refresh['user_id'], slug=slug)
                        # else:
                        #     post = Posts()
                        #     if user1 is not None:
                        #         # for obj in categories:
                        #         if user1.is_active:

                        #             post.user = user1
                        #             post.title = title
                        #             post.meta = meta
                        #             post.description = description
                        #             post.category = category.split(',')
                        #             if test_image is not None:
                        #                 post.have_image = True
                        #             print(post)
                        #             post.save()
                        #             return Response({"message": "Post Created"}, status=status.HTTP_200_OK)
                        #         return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message": "You are not a creator!"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception:
                    return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"message": "Story Detail exceeds max size limit."}, status=status.HTTP_400_BAD_REQUEST)


class AuthorOtherPostsListView(generics.ListAPIView):
    # authentication_classes = []
    permission_classes = [AllowAny,]
    pagination_class = StandardResultsSetPagination
    queryset = Posts.objects.all()
    serializer_class = AccountAllPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        slug = self.request.query_params.get('slug')
        print(slug)
        sus_posts = SuspendedPost.objects.all().values_list('post', flat=True)
        try:
            queryset = Posts.objects.filter(
                ~Q(id__in=sus_posts), ~Q(slug=slug)).order_by("-date")
            print(queryset)
            return queryset
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SearchApiView(APIView):
    # authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data.get('username', None)
        data1 = request.data.get('query', None)
        print(data)
        print(data1)
        people = Posts.objects.filter(Q(user__username=data))
        print(people)
        return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


# class RecentlyViewedView(generics.ListCreateAPIView):
#     # authentication_classes = []
#     permission_classes = []
#     pagination_class = StandardResultsSetPagination
#     queryset = RecentlyView.objects.all()
#     serializer_class = RecentlyViewSerializer
#     # filter_backends=[filters.SearchFilter]
#     # search_fields=['title','meta',
#     #         'slug',]

#     def get_queryset(self):
#         user1 = self.request.query_params.get('user')
#         # print(user1)
#         if self.request.user.is_active:
#             try:
#                 queryset = RecentlyView.objects.filter(
#                     Q(user=user1)).order_by("-date")
#                 # print(queryset)
#                 return queryset
#             except:
#                 return []
#         return []

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user": self.request.query_params.get('user')
#             }
#         )
#         return context


# class LikedPostView(generics.ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#     queryset = Follow.objects.all()
#     serializer_class = RecentlyViewSerializer

#     def get_queryset(self):
#         user1 = self.request.query_params.get('user')
#         # print(user1)
#         try:
#             queryset = Follow.objects.filter(Q(user=user1)).order_by("-date")
#             # print(queryset)
#             return queryset
#         except:
#             return []

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user": self.request.query_params.get('user')
#             }
#         )
#         return context


# class ArticleReportCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         # print(data["user"])
#         # print(data["report"])
#         # print(data["color"])
#         case = request.data.get('color', None)
#         user = get_object_or_404(User, username=data["user"])
#         # print(user)
#         report = get_object_or_404(Posts, slug=data["report"])
#         # print(report)
#         try:
#             if case is not None:
#                 data = ArticleReport()
#                 data.user = user
#                 data.report = report
#                 data.case = case
#                 data.save()
#             else:
#                 data = ArticleReport()
#                 data.user = user
#                 data.report = report
#                 data.save()
#             # print("created")
#             return Response(status=status.HTTP_201_CREATED)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class CommentReportCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         # print(data["user"])
#         # print(data["report"])
#         # print(data["color"])
#         case = request.data.get('color', None)
#         user = get_object_or_404(User, username=data["user"])
#         report = get_object_or_404(Comment, uniqued=data["report"])
#         try:
#             if case is not None:
#                 data = CommentReport()
#                 data.user = user
#                 data.report = report
#                 data.case = case
#                 data.save()
#             else:
#                 data = CommentReport()
#                 data.user = user
#                 data.report = report
#                 data.save()
#             # print("created")
#             return Response(status=status.HTTP_201_CREATED)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class ArticleMuteList(generics.ListAPIView):
#     # authentication_classes = []
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = ArticleMute.objects.all()
#     serializer_class = ArticleMuteSerializer


# class ArticleMuteDistinctList(generics.ListAPIView):
#     # authentication_classes = []
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = ArticleMute.objects.all()
#     serializer_class = ArticleMuteDisSerializer
#     pagination_class = StandardResultsSetPagination

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         test = get_object_or_404(User, username=user)
#         try:
#             signal = ArticleMute.objects.filter(user__username=user).exists()
#             if signal:
#                 queryset = ArticleMute.objects.filter(
#                     user__username=user).order_by('-date')
#                 print(queryset)
#                 return queryset
#             return []
#         except:
#             return []


# class ArticleMuteCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         print(data["user"])
#         print(data["mute"])
#         user = get_object_or_404(User, username=data["user"])
#         mute = get_object_or_404(Posts, slug=data["mute"])
#         try:
#             data1 = ArticleMute()
#             data1.user = user
#             data1.mute = mute
#             data1.save()
#             # print("created")
#             return Response(status=status.HTTP_201_CREATED)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class ArticleMuteDeleteView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         # print(data["user"])
#         # print(data["mute"])
#         user = get_object_or_404(User, username=data["user"])
#         mute = get_object_or_404(Posts, slug=data["mute"])
#         try:
#             if ArticleMute.objects.filter(user=user, mute=mute).exists():
#                 data = ArticleMute.objects.filter(user=user, mute=mute)
#                 data.delete()
#                 # print("deleted")
#                 return Response(status=status.HTTP_200_OK)
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


class ArticleUpdateView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        # print("edit user id-->", request.user.id)
        slug = request.data.get('slug', None)
        title = request.data.get('title', None)
        user = request.data.get('user', None)
        # print("user id-->", user)
        meta = request.data.get('meta', None)
        category = request.data.get('category', None)
        description = request.data.get('description', None)
        test1 = json.loads(description)
        size = asizeof.asizeof(test1)/1024
        if size < 1000:
            if title is None or slug is None or meta is None or description is None:
                return Response({"message": "There should be a slug/title/meta/description of the post."}, status=status.HTTP_400_BAD_REQUEST)
            if slug is not None and title is not None and meta is not None and description is not None and user is not None:

                if Posts.objects.filter(user__unique_id=user, slug=slug).exists():
                    post = Posts.objects.get(user__unique_id=user, slug=slug)
                    user1 = User.objects.get(unique_id=user)
                    test_image = firstImage(description)
                    if user1 is not None:
                        if user1.is_active:
                            try:
                                post.user = user1
                                post.title = title
                                post.meta = meta
                                post.description = description
                                post.category = category.split(',')
                                if test_image is not None:
                                    post.have_image = True
                                print(post)
                                post.save()
                                print("done")
                                return Response({"message": "Post Updated"}, status=status.HTTP_200_OK)
                            except:
                                return Response(status=status.HTTP_400_BAD_REQUEST)
                        return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)

                    return Response({"message": "Only Authorize users are allowed to Edit Articles"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "Post Doesn't Exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Title/Meta/Description should not be empty."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)


# class ArticleDeleteView(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []
#     queryset=Posts.objects.all()


class ArticleDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        user = request.data.get('user', None)
        # print("deleted slug", slug)
        # print("deleted user", user)
        # print("request user", str(request.user.id))
        if request.user.is_active:
            try:
                test = Posts.objects.filter(slug=slug).exists()
                if test:
                    if request.user.id == user:

                        post = Posts.objects.filter(slug=slug)
                        post.delete()
                        return Response({"message": "Post Deleted"}, status=status.HTTP_200_OK)
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)


class ArticleEditDetail(APIView):
    permission_classes = []
    authentication_classes = []
    # queryset = DraftPosts.objects.all()
    serializer_class = ArticleEditDetailSerializer

    def get(self, request, *args, **kwargs):
        slug = self.request.query_params.get('slug')
        print(slug)
        # user = self.request.headers.get('Authorization')
        # user1 = RefreshToken(user)
        # print(user1['user_id'])
        # user1=User.objects.get(username=user)
        # print(user1)
        # print(user1.id)
        # test = get_object_or_404(DraftPosts, slug=slug)
        try:
            queryset = Posts.objects.get(
                slug=slug)
            print(queryset.category)
            data = {
                "id": queryset.id,
                "title": queryset.title,
                "meta": queryset.meta,
                "description": queryset.description,
                "user": queryset.user.unique_id,
                "category": queryset.category
            }
            print("user->>", data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# class CommentListView(generics.ListAPIView):
#     permission_classes = []
#     queryset = Comment.objects.all()
#     serializer_class = CommentListSerializer


# class CommentDistinctListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Comment.objects.all()
#     serializer_class = CommentListDistinctSerializer
#     pagination_class= ArticlesStatsPagination

#     def get_queryset(self):
#         parent = self.request.query_params.get('parent')
#         user = self.request.query_params.get('user')
#         post = self.request.query_params.get('post')
#         try:
#             if user is None or user=="":
#                 return []
#             else:
#                 if parent is None:
#                     # print("no parent")
#                     queryset = Comment.objects.filter(Q(post__slug=post)& Q(parent=None))
#                     return queryset
#                 else:
#                     # print("parent")
#                     queryset = Comment.objects.filter(
#                         Q(post__slug=post)& Q(parent=parent)).order_by("-date")
#                     return queryset
#         except:
#             return []

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         # print(self.request.query_params.get('post'))
#         context.update(
#             {
#                 "post": self.request.query_params.get('post'),
#                 "parent": self.request.query_params.get('parent'),
#                 "user": self.request.query_params.get('user'),
#             }
#         )
#         return context


# class CommentDistinctView(APIView):
#     permission_classes = []
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         parent = request.data.get('parent', None)
#         user = request.data.get('user', None)
#         post = request.data.get('post', None)
#         # print("parent", parent)
#         # print("user", user)
#         # print("post", post)
#         try:
#             if parent is None:
#                 # print("no parent")
#                 queryset = Comment.objects.filter(post__slug=post, parent=None)
#             else:
#                 # print("parent")
#                 queryset = Comment.objects.filter(
#                     post__slug=post, parent=parent).order_by("-date")

#             data = CommentListDistinctSerializer(data=queryset, context={
#                                                 "request": request, 'user': user, 'parent': parent, 'post': post}, many=True)
#             data.is_valid()
#             # print("valid")
#             return Response(data.data, status=status.HTTP_200_OK)
#         except:
#             return Response(data.data, status=status.HTTP_400_BAD_REQUEST)


# class CommentUpdateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         _id = request.data.get('id', None)
#         text = request.data.get('text', None)
#         # print(_id)
#         # print(text)
#         test = get_object_or_404(Comment, id=_id)
#         if test:
#             data = Comment.objects.get(id=_id)
#             if request.user == data.user:
#                 try:
#                     data.user = data.user
#                     data.parent = data.parent
#                     data.post = data.post
#                     data.text = text
#                     data.save()
#                     return Response(status=status.HTTP_200_OK)
#                 except:
#                     return Response(status=status.HTTP_400_BAD_REQUEST)
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# class CommentCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         user = request.data.get('user', None)
#         # print("user-->", user)
#         # print("user-->", request.user)
#         text = request.data.get('text', None)
#         parent = request.data.get('parent', None)
#         post = request.data.get('post', None)
#         print(text)
#         print(parent)
#         print(post)
#         print(user)
#         if user is None or text is None or post is None:
#             print("1 called")
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if user == "" or text == "" or post == "":
#             print("2 called")
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         if parent is None or parent == "":
#             try:
#                 if str(request.user) == user:
#                     print("3 called")
#                     user = get_object_or_404(User, username=user)
#                     post = get_object_or_404(Posts, slug=post)
#                     comment = Comment()
#                     comment.user = user
#                     comment.post = post
#                     comment.parent = None
#                     comment.text = text
#                     comment.save()
#                     # print("if created")
#                     return Response(status=status.HTTP_201_CREATED)
#             except:
#                 print("4 called")
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             if str(request.user) == user:
#                 try:
#                     print("5 called")
#                     user = get_object_or_404(User, username=user)
#                     post = get_object_or_404(Posts, slug=post)
#                     parent = get_object_or_404(Comment, id=parent)
#                     comment = Comment()
#                     comment.user = user
#                     comment.post = post
#                     comment.parent = parent
#                     comment.text = text
#                     comment.save()
#                     # print("else created")
#                     return Response(status=status.HTTP_201_CREATED)
#                 except:
#                     print("6 called")
#                     return Response(status=status.HTTP_400_BAD_REQUEST)
#             print("7 called")
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         return Response(status=status.HTTP_400_BAD_REQUEST)

# # class CommentDeleteView(generics.DestroyAPIView):
# #     permission_classes = [permissions.IsAuthenticated]
# #     # authentication_classes = []
# #     queryset=Comment.objects.all()


# class CommentDeleteView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         _id = request.data.get('id', None)
#         # print("deleted id", _id)
#         # print("request user", str(request.user))
#         try:
#             test = Comment.objects.filter(id=_id).exists()
#             if test:
#                 comment = Comment.objects.get(id=_id)
#                 # print("author-->", comment.user)
#                 if request.user == comment.user:
#                     comment.delete()
#                     return Response({"message": "Comment Deleted"}, status=status.HTTP_200_OK)
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#             return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class ArticlesStateView(generics.ListAPIView):
#     queryset = Posts.objects.all()
#     serializer_class = ArticlesStatsGeneralSerializer
#     pagination_class = ArticlesStatsPagination
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         try:
#             test = Posts.objects.filter(user__username=user).exists()
#             if test:
#                 queryset = Posts.objects.filter(user__username=user)
#                 print(queryset)
#                 return queryset
#             return []
#         except:
#             return []


# class ArticlesAccView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Posts.objects.all()
#     serializer_class = ArticlesAccGeneralSerializer
#     pagination_class = ArticlesStatsPagination

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         try:
#             if str(self.request.user) == user:
#                 test = Posts.objects.filter(user__username=user).exists()
#                 if test:
#                     queryset = Posts.objects.filter(
#                         user__username=user).order_by('-date')
#                     # print(queryset)
#                     return queryset
#                 return []
#             else:
#                 raise ValidationError(status.HTTP_401_UNAUTHORIZED)
#         except:
#             return []
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)


# class CommentStateView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Comment.objects.all()
#     serializer_class = CommentsStatsGeneralSerializer
#     pagination_class = ArticlesStatsPagination

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         try:
#             test = Comment.objects.filter(user__username=user).exists()
#             if test:
#                 queryset = Comment.objects.filter(user__username=user)
#                 # print(queryset)
#                 return queryset
#             return []
#         except:
#             return []


# class CommentAccView(generics.ListAPIView):
#     # authentication_classes = []
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Comment.objects.all()
#     serializer_class = CommentsAccGeneralSerializer
#     pagination_class = ArticlesStatsPagination

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         try:
#             test = Comment.objects.filter(user__username=user).exists()
#             if test:
#                 queryset = Comment.objects.filter(user__username=user)
#                 print(queryset)
#                 return queryset
#             return []
#         except:
#             return []


# class CommentLikeViewset(viewsets.ModelViewSet):
#     serializer_class = CommentLikeSerializer
#     queryset = CommentLike.objects.all()
#     filter_backends = (filters1.DjangoFilterBackend,)
#     filter_fields = ("user", "comment",)
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # print("like get called")
#         try:
#             likes = CommentLike.objects.all()
#             serializer = CommentLikeSerializer(likes)
#             return Response(serializer.data)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#     def create(self, request):
#         # print("like createView called")
#         try:
#             serializer = CommentLikeSerializer(data=request.data)
#             if serializer.is_valid():
#                 likes = serializer.create(request)
#                 if likes:
#                     return Response(status=status.HTTP_201_CREATED)
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         # print("like delete called")
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_204_NO_CONTENT)


# class NotificationsDistinctListView(generics.ListAPIView):
#     serializer_class = NotificationDistinctListSerializer
#     queryset = Notifications.objects.all()
#     pagination_class = ArticlesStatsPagination
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = []

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         # print(user)
#         # user1=User.objects.get(username=user)
#         # print(user1)
#         # print(user1.id)
#         try:
#             test = Notifications.objects.filter(
#                 reciever__user__username=user).exists()

#             if test:
#                 Notifications.objects.filter(
#                             reciever__user__username=user).update(seen=True)
#                 queryset = Notifications.objects.filter(reciever__user__username=user).exclude(
#                     sender__user__username=user).order_by('-date')
#                 return queryset
#             return []
#         except:
#             return []


# class DoSeenNotifications(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         user = request.data.get('user', None)
#         try:
#             if user is not None and user != "":
#                 if str(request.user) == user:
#                     test = Notifications.objects.filter(
#                         reciever__user__username=user).exists()
#                     if test:
#                         Notifications.objects.filter(
#                             reciever__user__username=user).update(seen=True)
#                         return Response(status=status.HTTP_200_OK)
#                     else:
#                         return Response(status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response(status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class DashboardView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def get(self, request):
#         # print("dashboard called")
#         yesterday=date.today()-timedelta(days=1)
#         prev_month=date.today().month - 1
#         today_test=date.today().month
#         # present_year=date.today().year
#         # print(present_year)
#         data_test=[]
#         # count=today_test-1
#         for i in range(1,today_test+1,+1):
#             views_test=RecentlyView.objects.filter(date__month=i).count()
#             data_test.append(str(views_test))
#             # print("views-->",views_test)
#             # print("month-->",i)
#         # print("data_test",data_test)
#         Total_views=RecentlyView.objects.all().count()
#         Total_visits=GeneralUserAppInfo.objects.all().values_list('ip').distinct().count()
#         viewsT=RecentlyView.objects.filter(date__date=date.today()).count()
#         viewsY=RecentlyView.objects.filter(date__date=yesterday).count()
#         viewsM=RecentlyView.objects.filter(date__month=date.today().month).count()
#         viewsMY=RecentlyView.objects.filter(date__month=prev_month).count()
#         visitsT=GeneralUserAppInfo.objects.filter(date__date=date.today()).values_list('ip').distinct().count()
#         visitsY=GeneralUserAppInfo.objects.filter(date__date=yesterday).values_list('ip').distinct().count()
#         visitsM=GeneralUserAppInfo.objects.filter(date__month=date.today().month).values_list('ip').distinct().count()
#         visitsMY=GeneralUserAppInfo.objects.filter(date__month=prev_month).values_list('ip').distinct().count()
#         registerT=User.objects.filter(created_at__date=date.today()).count()
#         registerY=User.objects.filter(created_at__date=yesterday).count()
#         registerM=User.objects.filter(created_at__month=date.today().month).count()
#         registerMY=User.objects.filter(created_at__month=prev_month).count()
#         reportedAcc=UserReport.objects.filter(date__date=date.today()).count()
#         reportedAccY=UserReport.objects.filter(date__date=yesterday).count()
#         reportedAccM=UserReport.objects.filter(date__month=date.today().month).count()
#         reportedAccMY=UserReport.objects.filter(date__month=prev_month).count()
#         reportedArt=ArticleReport.objects.filter(date__date=date.today()).count()
#         reportedArtY=ArticleReport.objects.filter(date__date=yesterday).count()
#         reportedArtM=ArticleReport.objects.filter(date__month=date.today().month).count()
#         reportedArtMY=ArticleReport.objects.filter(date__month=prev_month).count()
#         suspendedAcc=SuspendAccounts.objects.filter(date__date=date.today()).count()
#         suspendedAccY=SuspendAccounts.objects.filter(date__date=yesterday).count()
#         suspendedAccM=SuspendAccounts.objects.filter(date__month=date.today().month).count()
#         suspendedAccMY=SuspendAccounts.objects.filter(date__month=prev_month).count()
#         suspendedArt=SuspendArticles.objects.filter(date__date=date.today()).count()
#         suspendedArtY=SuspendArticles.objects.filter(date__date=yesterday).count()
#         suspendedArtM=SuspendArticles.objects.filter(date__month=date.today().month).count()
#         suspendedArtMY=SuspendArticles.objects.filter(date__month=prev_month).count()
#         deletedAcc=DeletedAccounts.objects.filter(date__date=date.today()).count()
#         deletedAccY=DeletedAccounts.objects.filter(date__date=yesterday).count()
#         deletedAccM=DeletedAccounts.objects.filter(date__month=date.today().month).count()
#         deletedAccMY=DeletedAccounts.objects.filter(date__month=prev_month).count()
#         _copyright=Copyright.objects.filter(date__date=date.today()).count()
#         _copyrightY=Copyright.objects.filter(date__date=yesterday).count()
#         _copyrightM=Copyright.objects.filter(date__month=date.today().month).count()
#         _copyrightMY=Copyright.objects.filter(date__month=prev_month).count()
#         counterCopyright=CounterCopyright.objects.filter(date__date=date.today()).count()
#         counterCopyrightY=CounterCopyright.objects.filter(date__date=yesterday).count()
#         counterCopyrightM=CounterCopyright.objects.filter(date__month=date.today().month).count()
#         counterCopyrightMY=CounterCopyright.objects.filter(date__month=prev_month).count()
#         contactUsT=ContactUs.objects.filter(date__date=date.today()).count()
#         contactUsY=ContactUs.objects.filter(date__date=yesterday).count()
#         contactUsM=ContactUs.objects.filter(date__month=date.today().month).count()
#         contactUsMY=ContactUs.objects.filter(date__month=prev_month).count()
#         ###############################
#         viewsTPer=None
#         viewsMPer=None
#         visitsTPer=None
#         visitsMPer=None
#         registerTPer=None
#         registerMPer=None
#         reportedAccPer=None
#         reportedAccPerM=None
#         reportedArtPer=None
#         reportedArtMPer=None
#         suspendedAccPer=None
#         suspendedAccMPer=None
#         suspendedArtPer=None
#         suspendedArtMPer=None
#         deletedAccPer=None
#         deletedAccMPer=None
#         copyrightPer=None
#         copyrightMPer=None
#         counterCopyrightPer=None
#         counterCopyrightMPer=None
#         contactUsTPer=None
#         contactUsMPer=None
#         ###############################
#         viewsTSig=True
#         viewsMSig=True
#         visitsTSig=True
#         visitsMSig=True
#         registerMSig=True
#         registerTSig=True
#         reportedAccSig=True
#         reportedAccMSig=True
#         reportedArtSig=True
#         reportedArtMSig=True
#         suspendedAccSig=True
#         suspendedAccMSig=True
#         suspendedArtSig=True
#         suspendedArtMSig=True
#         deletedAccSig=True
#         deletedAccMSig=True
#         copyrightSig=True
#         copyrightMSig=True
#         counterCopyrightSig=True
#         counterCopyrightMSig=True
#         contactUsTSig=True
#         contactUsMSig=True
#         ##################
#         try:
#             if viewsT>viewsY:
#                 viewsTPer=viewsT-viewsY
#                 viewsTPer=(viewsTPer/viewsY)*100
#             if viewsT<viewsY:
#                 viewsTPer=viewsY-viewsT
#                 viewsTPer=(viewsTPer/viewsY)*100
#                 viewsTSig=False
#         except:
#             viewsTPer=0
#         try:
#             if viewsM>viewsMY:
#                 viewsMPer=viewsM-viewsMY
#                 viewsMPer=(viewsMPer/viewsMY)*100
#             if viewsM<viewsMY:
#                 viewsMPer=viewsMY-viewsM
#                 viewsMPer=(viewsMPer/viewsMY)*100
#                 viewsMSig=False
#             # viewsMPer=(viewsM/RecentlyView.objects.filter(date__month=prev_month).count())*100
#         except:
#             viewsMPer=0
#         try:
#             if visitsT>visitsY:
#                 visitsTPer=visitsT-visitsY
#                 visitsTPer=(visitsTPer/visitsY)*100
#             if visitsT<visitsY:
#                 visitsTPer=visitsY-visitsT
#                 visitsTPer=(visitsTPer/visitsY)*100
#                 visitsTSig=False
#             # visitsTPer=(visitsT/GeneralUserAppInfo.objects.filter(date__date=yesterday).values_list('ip').distinct().count())*100
#         except:
#             visitsTPer=0
#         try:
#             if visitsM>visitsMY:
#                 visitsMPer=visitsM-visitsMY
#                 visitsMPer=(visitsMPer/visitsMY)*100
#             if visitsM<visitsMY:
#                 visitsMPer=visitsMY-visitsM
#                 visitsMPer=(visitsMPer/visitsMY)*100
#                 visitsMSig=False
#             # visitsMPer=(visitsM/GeneralUserAppInfo.objects.filter(date__month=prev_month).values_list('ip').distinct().count())*100
#         except:
#             visitsMPer=0
#         try:
#             if registerT>registerY:
#                 registerTPer=registerT-registerY
#                 registerTPer=(registerTPer/registerY)*100
#             if registerT<registerY:
#                 registerTPer=registerY-registerT
#                 registerTPer=(registerTPer/registerY)*100
#                 registerTSig=False
#             # registerTPer=(registerT/User.objects.filter(created_at__date=yesterday).count())*100
#         except:
#             registerTPer=0
#         try:
#             if registerM>registerMY:
#                 registerMPer=registerM-registerMY
#                 registerMPer=(registerMPer/registerMY)*100
#             if registerM<registerMY:
#                 registerMPer=registerMY-registerM
#                 registerMPer=(registerMPer/registerMY)*100
#                 registerMSig=False
#             # registerMPer=(registerM/User.objects.filter(created_at__month=prev_month).count())*100
#         except:
#             registerMPer=0
#         try:
#             if reportedAcc>reportedAccY:
#                 reportedAccPer=reportedAcc-reportedAccY
#                 reportedAccPer=(reportedAccPer/reportedAccY)*100
#             if reportedAcc<reportedAccY:
#                 reportedAccPer=reportedAccY-reportedAcc
#                 reportedAccPer=(reportedAccPer/reportedAccY)*100
#                 reportedAccSig=False
#             # reportedAccPer=(reportedAcc/UserReport.objects.filter(date__date=yesterday).count())*100
#         except:
#             reportedAccPer=0
#         try:
#             if reportedAccM>reportedAccMY:
#                 reportedAccPerM=reportedAccM-reportedAccMY
#                 reportedAccPerM=(reportedAccPerM/reportedAccMY)*100
#             if reportedAccM<reportedAccMY:
#                 reportedAccPerM=reportedAccMY-reportedAccM
#                 reportedAccPerM=(reportedAccPerM/reportedAccMY)*100
#                 reportedAccMSig=False
#             # reportedAccPerM=(reportedAccM/UserReport.objects.filter(date__month=prev_month).count())*100
#         except:
#             reportedAccPerM=0
#         try:
#             if reportedArt>reportedArtY:
#                 reportedArtPer=reportedArt-reportedArtY
#                 reportedArtPer=(reportedArtPer/reportedArtY)*100
#             if reportedArt<reportedArtY:
#                 reportedArtPer=reportedArtY-reportedArt
#                 reportedArtPer=(reportedArtPer/reportedArtY)*100
#                 reportedArtSig=False
#             # reportedArtPer=(reportedArt/ArticleReport.objects.filter(date__date=yesterday).count())*100
#         except:
#             reportedArtPer=0
#         try:
#             if reportedArtM>reportedArtMY:
#                 reportedArtMPer=reportedArtM-reportedArtMY
#                 reportedArtMPer=(reportedArtMPer/reportedArtMY)*100
#             if reportedArtM<reportedArtMY:
#                 reportedArtMPer=reportedArtMY-reportedArtM
#                 reportedArtMPer=(reportedArtMPer/reportedArtMY)*100
#                 reportedArtMSig=False
#             # reportedArtMPer=(reportedArtM/ArticleReport.objects.filter(date__month=prev_month).count())*100
#         except:
#             reportedArtMPer=0
#         try:
#             if suspendedAcc>suspendedAccY:
#                 suspendedAccPer=suspendedAcc-suspendedAccY
#                 suspendedAccPer=(suspendedAccPer/suspendedAccY)*100
#             if suspendedAcc<suspendedAccY:
#                 suspendedAccPer=suspendedAccY-suspendedAcc
#                 suspendedAccPer=(suspendedAccPer/suspendedAccY)*100
#                 suspendedAccSig=False
#             # suspendedAccPer=(suspendedAcc/SuspendAccounts.objects.filter(date__date=yesterday).count())*100
#         except:
#             suspendedAccPer=0
#         try:
#             if suspendedAccM>suspendedAccMY:
#                 suspendedAccMPer=suspendedAccM-suspendedAccMY
#                 suspendedAccMPer=(suspendedAccMPer/suspendedAccMY)*100
#             if suspendedAccM<suspendedAccMY:
#                 suspendedAccMPer=suspendedAccMY-suspendedAccM
#                 suspendedAccMPer=(suspendedAccMPer/suspendedAccMY)*100
#                 suspendedAccMSig=False

#             # suspendedAccMPer=(suspendedAccM/SuspendAccounts.objects.filter(date__month=prev_month).count())*100
#         except:
#             suspendedAccMPer=0
#         try:
#             if suspendedArt>suspendedArtY:
#                 suspendedArtPer=suspendedArt-suspendedArtY
#                 suspendedArtPer=(suspendedArtPer/suspendedArtY)*100
#             if suspendedArt<suspendedArtY:
#                 suspendedArtPer=suspendedArtY-suspendedArt
#                 suspendedArtPer=(suspendedArtPer/suspendedArtY)*100
#                 suspendedArtSig=False
#             # suspendedArtPer=(suspendedArt/SuspendArticles.objects.filter(date__date=yesterday).count())*100
#         except:
#             suspendedArtPer=0
#         try:
#             if suspendedArtM>suspendedArtMY:
#                 suspendedArtMPer=suspendedArtM-suspendedArtMY
#                 suspendedArtMPer=(suspendedArtMPer/suspendedArtMY)*100
#             if suspendedArtM<suspendedArtMY:
#                 suspendedArtMPer=suspendedArtMY-suspendedArtM
#                 suspendedArtMPer=(suspendedArtMPer/suspendedArtMY)*100
#                 suspendedArtMSig=False
#             # suspendedArtMPer=(suspendedAccM/SuspendArticles.objects.filter(date__month=prev_month).count())*100
#         except:
#             suspendedArtMPer=0
#         try:
#             if deletedAcc>deletedAccY:
#                 deletedAccPer=deletedAcc-deletedAccY
#                 deletedAccPer=(deletedAccPer/deletedAccY)*100
#             if deletedAcc<deletedAccY:
#                 deletedAccPer=deletedAccY-deletedAcc
#                 deletedAccPer=(deletedAccPer/deletedAccY)*100
#                 deletedAccSig=False
#             # deletedAccPer=(deletedAcc/DeletedAccounts.objects.filter(date__date=yesterday).count())*100
#         except:
#             deletedAccPer=0
#         try:
#             if deletedAccM>deletedAccMY:
#                 deletedAccMPer=deletedAccM-deletedAccMY
#                 deletedAccMPer=(deletedAccMPer/deletedAccMY)*100
#             if deletedAccM<deletedAccMY:
#                 deletedAccMPer=deletedAccMY-deletedAccM
#                 deletedAccMPer=(deletedAccMPer/deletedAccMY)*100
#                 deletedAccMSig=False
#             # deletedAccM
#             # deletedAccMPer=(deletedAccM/DeletedAccounts.objects.filter(date__month=prev_month).count())*100
#         except:
#             deletedAccMPer=0
#         try:
#             if _copyright>_copyrightY:
#                 copyrightPer=_copyright-_copyrightY
#                 copyrightPer=(copyrightPer/_copyrightY)*100
#             if _copyright<_copyrightY:
#                 copyrightPer=_copyrightY-_copyright
#                 copyrightPer=(copyrightPer/_copyrightY)*100
#                 copyrightSig=False

#             # copyrightPer=(_copyright/Copyright.objects.filter(date__date=yesterday).count())*100
#         except:
#             copyrightPer=0
#         try:
#             if _copyrightM>_copyrightMY:
#                 copyrightMPer=_copyrightM-_copyrightMY
#                 copyrightMPer=(copyrightMPer/_copyrightMY)*100
#             if _copyrightM<_copyrightMY:
#                 copyrightMPer=_copyrightMY-_copyrightM
#                 copyrightMPer=(copyrightMPer/_copyrightMY)*100
#                 copyrightMSig=False

#             # copyrightMPer=(_copyrightM/Copyright.objects.filter(date__month=prev_month).count())*100
#         except:
#             copyrightMPer=0
#         try:
#             if counterCopyright>counterCopyrightY:
#                 counterCopyrightPer=counterCopyright-counterCopyrightY
#                 counterCopyrightPer=(counterCopyrightPer/counterCopyrightY)*100
#             if counterCopyright<counterCopyrightY:
#                 counterCopyrightPer=counterCopyrightY-counterCopyright
#                 counterCopyrightPer=(counterCopyrightPer/counterCopyrightY)*100
#                 counterCopyrightSig=False
#             # counterCopyrightPer=(counterCopyright/Copyright.objects.filter(date__date=yesterday).count())*100
#         except:
#             counterCopyrightPer=0
#         try:
#             if counterCopyrightM>counterCopyrightMY:
#                 counterCopyrightMPer=counterCopyrightM-counterCopyrightMY
#                 counterCopyrightMPer=(counterCopyrightMPer/counterCopyrightMY)*100
#             if counterCopyrightM<counterCopyrightMY:
#                 counterCopyrightMPer=counterCopyrightMY-counterCopyrightM
#                 counterCopyrightMPer=(counterCopyrightMPer/counterCopyrightMY)*100
#                 counterCopyrightMSig=False
#             # counterCopyrightMPer=(counterCopyrightM/Copyright.objects.filter(date__month=prev_month).count())*100
#         except:
#             counterCopyrightMPer=0
#         try:
#             if contactUsT>contactUsY:
#                 contactUsTPer=contactUsT-contactUsY
#                 contactUsTPer=(contactUsTPer/contactUsY)*100
#             if contactUsT<contactUsY:
#                 contactUsTPer=contactUsY-contactUsT
#                 contactUsTPer=(contactUsTPer/contactUsY)*100
#                 contactUsTSig=False

#             # contactUsTPer=(contactUsT/ContactUs.objects.filter(date__date=yesterday).count())*100
#         except:
#             contactUsTPer=0
#         try:
#             if contactUsM>contactUsMY:
#                 contactUsMPer=contactUsM-contactUsMY
#                 contactUsMPer=(contactUsMPer/contactUsMY)*100
#             if contactUsM<contactUsMY:
#                 contactUsMPer=contactUsMY-contactUsM
#                 contactUsMPer=(contactUsMPer/contactUsMY)*100
#                 contactUsMSig=False

#             # contactUsMPer=(contactUsM/ContactUs.objects.filter(date__month=prev_month).count())*100
#         except:
#             contactUsMPer=0
#         data = {'total_visits':Total_visits,'total_views':Total_views,'viewsT':viewsT,'viewsTPer':viewsTPer,'viewsTSig':viewsTSig,'viewsM':viewsM,
#         'viewsMPer':viewsMPer,'viewsMSig':viewsMSig,'visitsT':visitsT,'visitsTPer':visitsTPer,
#         'visitsTSig':visitsTSig,'visitsM':visitsM,'visitsMPer':visitsMPer,'visitsMSig':visitsMSig,
#         'registerM':registerM,'registerMPer':registerMPer,'registerMSig':registerMSig,'registerT':registerT,
#         'registerTPer':registerTPer,'registerTSig':registerTSig,'reportedAcc':reportedAcc,'reportedAccPer':reportedAccPer,
#         'reportedAccSig':reportedAccSig,'reportedAccM':reportedAccM,'reportedAccPerM':reportedAccPerM,
#         'reportedAccMSig':reportedAccMSig,'reportedArt':reportedArt,'reportedArtPer':reportedArtPer,'reportedArtSig':reportedArtSig,
#         'reportedArtM':reportedArtM,'reportedArtMPer':reportedArtMPer,'reportedArtMSig':reportedArtMSig,
#         'suspendedAcc':suspendedAcc,'suspendedAccPer':suspendedAccPer,'suspendedAccSig':suspendedAccSig,
#         'suspendedAccM':suspendedAccM,'suspendedAccMPer':suspendedAccMPer,'suspendedAccMSig':suspendedAccMSig,'suspendedArt':suspendedArt,
#         'suspendedArtPer':suspendedArtPer,'suspendedArtSig':suspendedArtSig,'suspendedArtM':suspendedArtM,
#         'suspendedArtMPer':suspendedArtMPer,'suspendedArtMSig':suspendedArtMSig,'deletedAcc':deletedAcc,'deletedAccPer':deletedAccPer,
#         'deletedAccSig':deletedAccSig,'deletedAccM':deletedAccM,'deletedAccMPer':deletedAccMPer,
#         'deletedAccMSig':deletedAccMSig,'_copyright':_copyright,'copyrightPer':copyrightPer,'copyrightSig':copyrightSig,
#         '_copyrightM':_copyrightM,'copyrightMPer':copyrightMPer,'copyrightMSig':copyrightMSig,
#         'counterCopyright':counterCopyright,'counterCopyrightPer':counterCopyrightPer,'counterCopyrightSig':counterCopyrightSig,
#         'counterCopyrightM':counterCopyrightM,'counterCopyrightMPer':counterCopyrightMPer,'counterCopyrightMSig':counterCopyrightMSig,
#         'contactUsT':contactUsT,'contactUsTPer':contactUsTPer,'contactUsTSig':contactUsTSig,'contactUsM':contactUsM,
#         'contactUsMPer':contactUsMPer,'contactUsMSig':contactUsMSig}
#         # data=DashboardSerializer()
#         # print("data-->",data.data)
#         return Response(data,status=status.HTTP_202_ACCEPTED)


# class ReportedArticles(generics.ListAPIView):
#     serializer_class = ReportedArticlesSerializer
#     queryset = ArticleReport.objects.all()
#     pagination_class = ArticlesStaffPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         user=self.request.query_params.get('user')
#         try:
#             if user=="" or user is None:
#                 queryset=ArticleReport.objects.all().order_by('-date')
#                 return queryset
#             else:
#                 queryset=ArticleReport.objects.filter(Q(id__icontains=user)|Q(user__email__icontains=user)|Q(user__username__icontains=user)|Q(user__name__icontains=user)|Q(report__user__email__icontains=user)|Q(report__user__username__icontains=user)|Q(report__user__name__icontains=user)|Q(case__icontains=user)|Q(report__title__icontains=user)|Q(report__slug__icontains=user)).order_by('-date')
#                 return queryset
#         except:
#             return []

# class ReportedComments(generics.ListAPIView):
#     serializer_class = ReportedCommentsSerializer
#     queryset = CommentReport.objects.all()
#     pagination_class = ArticlesStatsPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         user=self.request.query_params.get('user')
#         try:
#             if user=="" or user is None:
#                 queryset=CommentReport.objects.all().order_by('-date')
#                 return queryset
#             else:
#                 queryset=CommentReport.objects.filter(Q(id__icontains=user)|Q(user__email__icontains=user)|Q(user__username__icontains=user)|Q(user__name__icontains=user)|Q(report__user__email__icontains=user)|Q(report__user__username__icontains=user)|Q(report__user__name__icontains=user)|Q(case__icontains=user)).order_by('-date')
#                 return queryset
#         except:
#             return []

# class DeleteReportedCommentRequestView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         try:
#             data=CommentReport.objects.filter(id=report)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class DeleteAllDisReportedCommentRequestView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         case = request.data.get('case', None)
#         try:
#             data=CommentReport.objects.filter(report=report,case=case)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class DeleteReportedCommentsView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         try:
#             data=Comment.objects.filter(id=report)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class DeleteReportedArticleView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         try:
#             data=ArticleReport.objects.filter(id=report)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class DeleteAllDistinctReportedArticleView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         case = request.data.get('case', None)
#         try:
#             data=ArticleReport.objects.filter(report=report,case=case)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class ActiveOrSuspendArticle(APIView):
#     permission_classes=[permissions.IsAdminUser]

#     def post(self, request, *args, **kwargs):
#         post = request.data.get('post', None)
#         if post is None or post=="":
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         else:
#             data=get_object_or_404(Posts,id=post)
#             p_url='https://www.sotiotalk.com/@'+data.user.username+'/'+data.slug
#             post_date=data.date.strftime("%b %d, %Y")
#             image=firstImage(data.description)
#             title=data.title
#             meta=data.meta
#             try:
#                 if data.suspended==True:
#                     data.suspended=False
#                     data.save()

#                     return Response(status=status.HTTP_200_OK)
#                 else:
#                     try:
#                         data.suspended=True
#                         data.save()
#                         homeUrl = 'https://www.sotiotalk.com/'
#                         contactUrl = 'https://www.sotiotalk.com/contact-us'
#                         rules = 'https://www.sotiotalk.com/legal'
#                         guidelines = 'https://www.sotiotalk.com/guidelines'
#                         _help = 'https://www.sotiotalk.com/help'
#                         policy = 'https://www.sotiotalk.com/legal/privacy-policy'
#                         data = {'to_email': data.user.email,
#                         'home': homeUrl,
#                         'p_url':p_url,
#                         'image':image,
#                         'title':title,
#                         'meta':meta,
#                         'help':_help,
#                         'policy':policy,
#                         'date':post_date,
#                         'contact': contactUrl,
#                         "rules":rules,
#                         'name':data.user.name,
#                         "guidelines":guidelines,
#                         'email_subject': 'Your Article is suspended.'}
#                         article_suspension_email_task.delay(data)
#                         return Response(status=status.HTTP_200_OK)
#                     except:
#                         return Response(status=status.HTTP_400_BAD_REQUEST)
#             except:
#                     return Response(status=status.HTTP_400_BAD_REQUEST)

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
        if image:
            return image
        return None
    except:
        return None


# class StaffPostSingleGetView(generics.ListAPIView):
#     serializer_class = StaffPostSingleSerializer
#     queryset = Posts.objects.all()
#     permission_classes = [permissions.IsAdminUser]
#     # authentication_classes = []

#     def get_queryset(self):
#         post = self.request.query_params.get('post')
#         try:
#             test = Posts.objects.filter(slug=post).exists()
#             if test:
#                 queryset = Posts.objects.filter(slug=post)
#                 return queryset
#             return []
#         except:
#             return []

# class SotioTalkArticlesView(generics.ListAPIView):
#     serializer_class = StaffArticlesSerializer
#     queryset = Posts.objects.all()
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['id', 'title','meta','slug']
#     pagination_class = StandardResultsSetPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         post=self.request.query_params.get('post')
#         try:
#             if post=="" or post is None:
#                 queryset=Posts.objects.all().order_by('-date')
#                 return queryset
#             else:
#                 queryset=Posts.objects.filter(Q(id__icontains=post)|Q(title__icontains=post)|Q(slug__icontains=post)|Q(meta__icontains=post)).order_by('-date')
#                 return queryset
#         except:
#             return []


# class SuspendedArticles(generics.ListAPIView):
#     serializer_class = SuspendedArticlesSerializer
#     queryset = SuspendArticles.objects.all()
#     pagination_class = ArticlesStaffPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         post=self.request.query_params.get('post')
#         try:
#             if post=="" or post is None:
#                 queryset=SuspendArticles.objects.all().order_by('-date')
#                 return queryset
#             else:
#                 queryset=SuspendArticles.objects.filter(Q(post__id__icontains=post)|Q(post__user__email__icontains=post)|Q(post__user__username__icontains=post)|Q(post__user__name__icontains=post)|Q(post__title__icontains=post)|Q(post__meta__icontains=post)|Q(post__slug__icontains=post)).order_by('-date')
#                 return queryset
#         except:
#             return []

# class ContactUsListView(generics.ListAPIView):
#     serializer_class = ContactUsListSerializer
#     queryset = ContactUs.objects.all()
#     pagination_class = StandardResultsSetPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         post=self.request.query_params.get('post')
#         try:
#             if post=="" or post is None:
#                 queryset=ContactUs.objects.all().order_by('-date')
#                 return queryset
#             else:
#                 queryset=ContactUs.objects.filter(Q(id__icontains=post)|Q(email__icontains=post)|Q(name__icontains=post)|Q(subject__icontains=post)).order_by('-date')
#                 return queryset
#         except:
#             return []

# class ContactUsSingleView(generics.ListAPIView):
#     serializer_class = ContactUsListSerializer
#     queryset = ContactUs.objects.all()
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         post=self.request.query_params.get('post')
#         try:
#             test = ContactUs.objects.filter(id=post).exists()
#             if test:
#                 queryset = ContactUs.objects.filter(id=post)
#                 return queryset
#             return []
#         except:
#             return []

# class DeleteContactUsView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request,*args,**kwargs):
#         report = request.data.get('id', None)
#         try:
#             data=ContactUs.objects.filter(id=report)
#             data.delete()
#             return Response(status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class AdminAccountPostsListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAdminUser]
#     pagination_class = StandardResultsSetPagination
#     queryset = Posts.objects.all()
#     serializer_class = StaffArticlesSerializer

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         post = self.request.query_params.get('post')
#         try:
#             if post=="" or post is None:
#                 test = get_object_or_404(User, username=user)
#                 queryset = Posts.objects.filter(user__username=user).order_by("-date")
#                 return queryset
#             else:
#                 test = get_object_or_404(User, username=user)
#                 queryset = Posts.objects.filter(user__username=user).filter(Q(title__icontains=post)|Q(slug__icontains=post)).order_by("-date")
#                 return queryset
#         except:
#             return []

# class UserComments(generics.ListAPIView):
#     serializer_class = AdminUserCommentSerializer
#     queryset = Comment.objects.all()
#     pagination_class = ArticlesStatsPagination
#     permission_classes=[permissions.IsAdminUser]

#     def get_queryset(self):
#         user=self.request.query_params.get('user')
#         search=self.request.query_params.get('search')
#         if user=="" or user is None:
#             return []
#         elif user is not None and user !="" and search is not None and search !="":
#             try:
#                 queryset=Comment.objects.filter(user__username=user).filter(Q(uniqued__icontains=search)).order_by('-date')
#                 return queryset
#             except:
#                 return []
#         else:
#             try:
#                 queryset=Comment.objects.filter(user__username=user).order_by('-date')
#                 return queryset
#             except:
#                 return []

# class AdminSavedArticlesListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAdminUser]
#     pagination_class = StandardResultsSetPagination
#     queryset = BookMark.objects.all()
#     serializer_class = StaffSavedArticlesSerializer

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         search=self.request.query_params.get('search')
#         if user=="" or user is None:
#             return []
#         elif user is not None and user !="" and search is not None and search !="":
#             try:
#                 queryset=BookMark.objects.filter(user__username=user).filter(Q(post__title__icontains=search)|Q(post__slug__icontains=search)|Q(post__user__username=search)|Q(post__user__name=search)|Q(post__user__email=search)|Q(post__user__unique_id=search)).order_by('-date')
#                 return queryset
#             except:
#                 return []
#         else:
#             try:
#                 queryset=BookMark.objects.filter(user__username=user).order_by('-date')
#                 return queryset
#             except:
#                 return []

# class AdminHistoryArticlesListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAdminUser]
#     pagination_class = StandardResultsSetPagination
#     queryset = RecentlyView.objects.all()
#     serializer_class = StaffHistoryArticlesSerializer

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         search=self.request.query_params.get('search')
#         if user=="" or user is None:
#             return []
#         elif user is not None and user !="" and search is not None and search !="":
#             try:
#                 queryset=RecentlyView.objects.filter(user__username=user).filter(Q(post__title__icontains=search)|Q(post__slug__icontains=search)|Q(post__user__username=search)|Q(post__user__name=search)|Q(post__user__email=search)|Q(post__user__unique_id=search)).order_by('-date')
#                 return queryset
#             except:
#                 return []
#         else:
#             try:
#                 queryset=RecentlyView.objects.filter(user__username=user).order_by('-date')
#                 return queryset
#             except:
#                 return []

# class AdminFollowArticlesListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAdminUser]
#     pagination_class = StandardResultsSetPagination
#     queryset = Follow.objects.all()
#     serializer_class = StaffLikedArticlesSerializer

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         search=self.request.query_params.get('search')
#         if user=="" or user is None:
#             return []
#         elif user is not None and user !="" and search is not None and search !="":
#             try:
#                 queryset=Follow.objects.filter(user__username=user).filter(Q(post__title__icontains=search)|Q(post__slug__icontains=search)|Q(post__user__username=search)|Q(post__user__name=search)|Q(post__user__email=search)|Q(post__user__unique_id=search)).order_by('-date')
#                 return queryset
#             except:
#                 return []
#         else:
#             try:
#                 queryset=Follow.objects.filter(user__username=user).order_by('-date')
#                 return queryset
#             except:
#                 return []

# class AdminSidebarCountView(APIView):
#     permission_classes=[permissions.IsAdminUser]
#     def get(self,request,*args,**kwargs):
#         try:
#             c_usernames=ChangedUsername.objects.all().count()
#             r_users=UserReport.objects.all().count()
#             r_articles=ArticleReport.objects.all().count()
#             r_responses=CommentReport.objects.all().count()
#             contact_us=ContactUs.objects.all().count()
#             copy=Copyright.objects.all().count()
#             c_copy=CounterCopyright.objects.all().count()
#             users=Profile.objects.all().count()
#             articles=Posts.objects.all().count()
#             s_users=SuspendAccounts.objects.all().count()
#             s_articles=SuspendArticles.objects.all().count()
#             d_users=Profile.objects.filter(deactivated=True).count()
#             del_users=DeletedAccounts.objects.all().count()
#             data={
#                 "c_usernames":c_usernames,
#                 "r_users":r_users,
#                 "r_articles":r_articles,
#                 "r_responses":r_responses,
#                 "contact_us":contact_us,
#                 "copy":copy,
#                 "c_copy":c_copy,
#                 "users":users,
#                 "articles":articles,
#                 "s_users":s_users,
#                 "s_articles":s_articles,
#                 "d_users":d_users,
#                 "del_users":del_users,
#             }
#             return Response(data,status=status.HTTP_200_OK)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class TotalAccountViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         # date3=request.data.get('date', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "views":RecentlyView.objects.filter(date__date=date1).filter(post__user__id=user).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)


# class PrevAccountViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "views":RecentlyView.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class NextAccountViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "views":RecentlyView.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class TotalAccountLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "likes":Follow.objects.filter(date__date=date1).filter(post__user__id=user).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)

# class PrevAccountLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "likes":Follow.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class NextAccountLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "likes":Follow.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class TotalAccountComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "comments":Comment.objects.filter(date__date=date1).filter(post__user__id=user).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)

# class PrevAccountComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "comments":Comment.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class NextAccountComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             print("date 3",date3)
#             print("today",date.today())
#             for x in range(0,30):
#                 print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "comments":Comment.objects.filter(post__user__id=user).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class TotalAccountViewsLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         user=request.data.get('user', None)
#         prev_month=date.today().month - 1
#         viewsM=RecentlyView.objects.filter(post__user__id=user).filter(date__month=date.today().month).count()
#         viewsMY=RecentlyView.objects.filter(post__user__id=user).filter(date__month=prev_month).count()
#         likesM=Follow.objects.filter(post__user__id=user).filter(date__month=date.today().month).count()
#         likesMY=Follow.objects.filter(post__user__id=user).filter(date__month=prev_month).count()
#         commentsM=Comment.objects.filter(post__user__id=user).filter(date__month=date.today().month).count()
#         commentsMY=Comment.objects.filter(post__user__id=user).filter(date__month=prev_month).count()
#         viewsMSig=True
#         viewsMPer=None
#         likesMSig=True
#         likesMPer=None
#         commentsMSig=True
#         commentsMPer=None
#         try:
#             if viewsM>viewsMY:
#                     viewsMPer=viewsM-viewsMY
#                     viewsMPer=(viewsMPer/viewsMY)*100
#             if viewsM<viewsMY:
#                 viewsMPer=viewsMY-viewsM
#                 viewsMPer=(viewsMPer/viewsMY)*100
#                 viewsMSig=False
#         except:
#             viewsMPer=0
#         try:
#             if likesM>likesMY:
#                     likesMPer=viewsM-viewsMY
#                     likesMPer=(likesMPer/viewsMY)*100
#             if likesM<likesMY:
#                 likesMPer=likesMY-likesM
#                 likesMPer=(likesMPer/likesMY)*100
#                 likesMSig=False
#         except:
#             likesMPer=0
#         try:
#             if commentsM>commentsMY:
#                     commentsMPer=viewsM-viewsMY
#                     commentsMPer=(commentsMPer/viewsMY)*100
#             if commentsM<commentsMY:
#                 commentsMPer=commentsMY-commentsM
#                 commentsMPer=(commentsMPer/commentsMY)*100
#                 commentsMSig=False
#         except:
#             commentsMPer=0
#         data={
#             "views":RecentlyView.objects.filter(post__user__id=user).count(),
#             "likes":Follow.objects.filter(post__user__id=user).count(),
#             "views_t_m":viewsM,
#             "views_t_m_p":viewsMPer,
#             "v_signal":viewsMSig,
#             "likes_t_m":likesM,
#             "likes_t_m_p":likesMPer,
#             "l_signal":likesMSig,
#             "comments_t_m":commentsM,
#             "comments_t_m_p":commentsMPer,
#             "c_signal":commentsMSig,
#         }
#         return Response({"data":data},status=status.HTTP_200_OK)

# class TotalArticleViewsLikesComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         obj=get_object_or_404(Posts,slug=post)
#         data={
#             "slug":obj.slug,
#             "title":obj.title,
#             "username":obj.user.username,
#             "date":obj.date.strftime("%b %d, %Y"),
#             "views":RecentlyView.objects.filter(post__slug=post).count(),
#             "likes":Follow.objects.filter(post__slug=post).count(),
#             "comments":Comment.objects.filter(post__slug=post).count(),
#         }
#         return Response({"data":data},status=status.HTTP_200_OK)

# class TotalArticleComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "comments":Comment.objects.filter(date__date=date1).filter(post__slug=post).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)


# class PrevArticleComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "comments":Comment.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class NextArticleComments(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "comments":Comment.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)


# class NextArticleLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "likes":Follow.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)


# class PrevArticleLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "likes":Follow.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)


# class TotalArticleLikes(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "likes":Follow.objects.filter(date__date=date1).filter(post__slug=post).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)

# class NextArticleViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)+timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "views":RecentlyView.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=stats
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class PrevArticleViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         date3=request.data.get('date', None)

#         stats=[]
#         if date3 is None or date3=="":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             year, month, day = map(int, date3.split('-'))
#             # print("date 3",date3)
#             # print("today",date.today())
#             for x in range(0,30):
#                 # print(x)
#                 date1=date(year, month, day)-timedelta(days=x)
#                 # print("date1",date1)
#                 dateT=date1.strftime("%b %d")
#                 # print(date)
#                 data_list={
#                     "date":date1,
#                     "dateT":dateT,
#                     "views":RecentlyView.objects.filter(post__slug=post).filter(date__date=date1).count()
#                 }
#                 stats.append(data_list)
#             stats1=list(reversed(stats))
#             return Response({"data":stats1},status=status.HTTP_200_OK)

# class TotalArticleViews(APIView):
#     permission_classes=[permissions.IsAuthenticated]

#     def post(self,request,*args,**kwargs):
#         post=request.data.get('post', None)
#         # date3=request.data.get('date', None)

#         stats=[]
#         for x in range(0,30):

#             date1=date.today()-timedelta(days=x)
#             dateT=date1.strftime("%b %d")
#             # print(date)
#             data_list={
#                 "date":date1,
#                 "dateT":dateT,
#                 "views":RecentlyView.objects.filter(date__date=date1).filter(post__slug=post).count()
#             }
#             stats.append(data_list)
#         stats1=list(reversed(stats))
#         return Response({"data":stats1},status=status.HTTP_200_OK)

# class ResponseDetailView(APIView):
#     permission_classes=[permissions.AllowAny]

#     def post(self,request,*args,**kwargs):
#         response=request.data.get('response', None)
#         user=request.data.get('user', None)
#         user1=request.data.get('user1', None)
#         # print(response)
#         # print(user)
#         obj=get_object_or_404(Comment,uniqued=response,user__username=user)
#         # print(obj.post)
#         # print(obj.parent)
#         image=get_object_or_404(Profile,user__username=user)
#         likes=0
#         liked=None
#         if not image.avatar:
#             image=None
#         else:
#             image=image.avatar.url
#         try:
#             follow_count=CommentLike.objects.filter(comment=obj).count()
#             likes= follow_count
#         except:
#             likes=0
#         try:
#             liked = CommentLike.objects.filter(comment=obj)
#             print(liked)
#             user1 = liked.filter(user__username=user1)
#             print(user1)
#             if user1:
#                 liked= True
#             else:
#                 liked=False
#         except:
#             liked=False
#         if obj.parent is None or obj.parent=="":
#             data={
#                 "url":f"/@{obj.post.user.username}/{obj.post.slug}",
#                 "name":obj.post.user.name,
#                 "parent_text":obj.post.title,
#                 "a_username":obj.user.username,
#                 "a_name":obj.user.name,
#                 "a_img":image,
#                 "text":obj.text,
#                 "id":obj.id,
#                 "post":obj.post.slug,
#                 "date":obj.date.strftime("%b %d, %Y"),
#                 "parent":obj.id,
#                 "likes":likes,
#                 "liked":liked
#             }
#             return Response(data,status=status.HTTP_200_OK)
#         else:
#             data={
#                 "url":f"/@{obj.parent.user.username}/responses/{obj.parent.uniqued}",
#                 "name":obj.parent.user.name,
#                 "parent_text":obj.parent.text,
#                 "a_username":obj.user.username,
#                 "a_name":obj.user.name,
#                 "a_img":image,
#                 "text":obj.text,
#                 "id":obj.id,
#                 "post":obj.post.slug,
#                 "date":obj.date.strftime("%b %d, %Y"),
#                 "parent":obj.id,
#                 "likes":likes,
#                 "liked":liked
#             }
#             return Response(data,status=status.HTTP_200_OK)

class LinkTool(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        html = Request(self.request.query_params.get('url'),
                       headers={'User-Agent': 'Mozilla/5.0'})
        try:
            web = urlopen(html).read()
            soup = BeautifulSoup(web)
            data = {
                "success": 1,
                "meta": {
                    "title": soup.find("meta", property="og:title")['content'],
                    "description": soup.find("meta", property="og:description")['content'],
                    "image": {
                        "url": str(soup.find("meta", property="og:image")['content'])
                    }
                }
            }
            return Response(data)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# class ViewsTrending(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = UsersStaffPagination
#     serializer_class = TrendingPostSerializer
#     queryset = Posts.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         if user is not None:
#             week_date=date.today()-timedelta(days=7)
#             tommorow=date.today()+timedelta(days=1)
#             query_posts=sorted(Posts.objects.filter(Q(date__gte=week_date)&Q(date__lte=tommorow)&Q(have_image=True)), key=lambda t: t.views,reverse=True)
#             query_posts2=list(filter(lambda t : t.views > 0 , query_posts))
#             trending_posts=list(query_posts2)[:3]
#             for item in trending_posts:
#                 obj=TrendingPosts()
#                 obj.post=item
#                 obj.user=item.user
#                 obj.save()

#             return query_posts2
#         else:
#             return []


#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user2": self.request.query_params.get('user'),
#             }
#         )
#         return context

# class LikesTrending(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = UsersStaffPagination
#     serializer_class = TrendingPostSerializer
#     queryset = Posts.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         if user is not None:
#             week_date=date.today()-timedelta(days=7)
#             tommorow=date.today()+timedelta(days=1)
#             query_posts=sorted(Posts.objects.filter(Q(date__gte=week_date)&Q(date__lte=tommorow)&Q(have_image=True)), key=lambda t: t.likes,reverse=True)
#             query_posts2=list(filter(lambda t : t.likes > 0 , query_posts))
#             trending_posts=list(query_posts2)[:3]
#             for item in trending_posts:
#                 obj=TrendingPosts()
#                 obj.post=item
#                 obj.user=item.user
#                 obj.save()

#             return query_posts2
#         else:
#             return []


#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user2": self.request.query_params.get('user'),
#             }
#         )
#         return context

# class CommentsTrending(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = UsersStaffPagination
#     serializer_class = TrendingPostSerializer
#     queryset = Posts.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         if user is not None:
#             week_date=date.today()-timedelta(days=7)
#             tommorow=date.today()+timedelta(days=1)
#             query_posts=sorted(Posts.objects.filter(Q(date__gte=week_date)&Q(date__lte=tommorow)&Q(have_image=True)), key=lambda t: t.comments,reverse=True)
#             print("obj",query_posts)
#             query_posts2=list(filter(lambda t : t.comments > 0 , query_posts))
#             print("obj2",query_posts2)
#             trending_posts=list(query_posts2)[:3]
#             for item in trending_posts:
#                 obj=TrendingPosts()
#                 obj.post=item
#                 obj.user=item.user
#                 obj.save()
#             print("last",query_posts2)

#             return query_posts2
#         else:
#             return []


#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user2": self.request.query_params.get('user'),
#             }
#         )
#         return context

# class WritersTrending(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = UsersStaffPagination
#     serializer_class = UserTrendingListSerializer
#     queryset = Profile.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         if user is not None:
#             week_date=date.today()-timedelta(days=7)
#             tomorrow = date.today() + timedelta(days=1)
#             query_posts2=TrendingPosts.objects.filter(Q(date__gte=week_date)&Q(date__lt=tomorrow)).values_list("user",flat=True)
#             query_posts2=list(query_posts2)
#             test_list1=[]
#             for _id in query_posts2:
#                 test_data1={
#                 'user':_id,
#                 'total':TrendingPosts.objects.filter(user__id=_id).count()
#                 }
#                 test_list1.append(test_data1)
#             sorted_list1=sorted(test_list1,key=lambda x:x['total'],reverse=True)
#             sorted_posts1=list(o['user'] for o in sorted_list1)
#             trending_users=Profile.objects.filter(user__id__in=sorted_posts1)

#             return trending_users
#         else:
#             return []


#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user2": self.request.query_params.get('user'),
#             }
#         )
#         return context

# class PostsCommentsTrending(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = UsersStaffPagination
#     serializer_class = CommentsTrendingSerializer
#     queryset = Comment.objects.all()

#     def get_queryset(self):
#         user = self.request.query_params.get('user')
#         if user is not None:
#             week_date=date.today()-timedelta(days=7)
#             tomorrow = date.today() + timedelta(days=1)
#             query_posts2=sorted(Comment.objects.filter(Q(date__gte=week_date)&Q(date__lt=tomorrow)&Q(parent__isnull=True)),key=lambda x:x.replies,reverse=True)
#             query_posts2=list(filter(lambda t : t.replies > 0 , query_posts2))
#             # test_list1=[]
#             # for _id in query_posts2:
#             #     test_data1={
#             #     'comment':_id,
#             #     'total':Comment.objects.filter(parent__id=_id).count() + Comment.objects.filter(parent__parent__id=_id).count()
#             #     }
#             #     test_list1.append(test_data1)

#             # sorted_list1=sorted(test_list1,key=lambda x:x['total'],reverse=True)
#             # sorted_list1=list(filter(lambda t : t.total > 0 , sorted_list1))
#             # sorted_posts1=list(o['comment'] for o in sorted_list1)
#             # trending_posts_comments=Comment.objects.filter(id__in=sorted_posts1)

#             return query_posts2
#         else:
#             return []


#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update(
#             {
#                 "user2": self.request.query_params.get('user'),
#             }
#         )
#         return context


class DraftPostsCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        title = request.data.get('title', None)
        user = request.data.get('user', None)
        meta = request.data.get('meta', None)
        description = request.data.get('description', None)
        slug = request.data.get('slug', None)
        read_min = request.data.get('read_min', None)
        category = request.data.get('category', None)
        category1 = json.loads(category)
        # print("category", category)
        test1 = json.loads(description)
        draft_post = DraftPosts()
        # print(title)
        # print(meta)
        print(slug)
        try:
            size = asizeof.asizeof(test1)/1024
            if size >= 1000:
                return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)
            if title is None or meta is None or description is None:
                return Response({"message": "There should be title/meta/description of the post."}, status=status.HTTP_400_BAD_REQUEST)
            if user is not None:
                refresh = RefreshToken(user)
                print(refresh['id'])
                if refresh['id'] is not None:
                    user1 = User.objects.get(id=refresh['id'])
                    is_active=user1.is_active # To Check if user is active
                    
                    # read_minP = ReadMinutesOfPosts()
                    checkP = DraftPosts.objects.filter(
                                user__id=refresh['id'], slug=slug) # To Check if there is any previous Draft Post Existed
                    is_checkP=not checkP # To Check if checkP is None or an object
                    # print("user",user1)
                    # print("checkP",checkP)
                    # print("checkP",not checkP)
                    
                    
                    try:
                        print("inside try")
                        if is_active:
                            print("is_active")
                            if is_checkP:
                                print("not checkP")
                                draft_post.user = user1
                                draft_post.title = title
                                draft_post.meta = meta
                                draft_post.description = description
                                draft_post.category = category1
                                draft_post.read_min = read_min
                                draft_post.save()
                                print(draft_post)
                                print("done")
                                    # if user1.isActive:
                                    #     checkP.user = user1
                                    #     checkP.title = title
                                    #     checkP.meta = meta
                                    #     checkP.description = description
                                    #     checkP.category = category1
                                    #     checkP.read_min = read_min
                                    #     print(checkP)
                                    #     checkP.save()
                                    #     print("done")

                                        # categoryP.post = checkP
                                        # categoryP.category = category1
                                        # categoryP.save()

                                        # print(categoryP)

                                        # read_minP.post = categoryP
                                        # read_minP.read_min = read_min
                                        # read_minP.save()
                                        # print(read_minP)
                                return Response({"message": "Draft Successfully Created"}, status=status.HTTP_200_OK)
                            else:
                                print("there is a post")
                                post = DraftPosts.objects.get(
                                    user__id=refresh['id'], slug=slug)
                                # post.user = user1
                                post.title = title
                                post.meta = meta
                                post.description = description
                                post.category = category1
                                post.read_min = read_min
                                print("post-->", post)
                                post.save()

                                    # categoryP.post = checkP
                                    # categoryP.category = category1
                                    # categoryP.save()

                                    # print(categoryP)

                                    # read_minP.post = categoryP
                                    # read_minP.read_min = read_min
                                    # read_minP.save()
                                    # print(read_minP)
                                return Response({"message": "Draft Post Updated"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception:
                        return Response({"message": "Annomouse Reason"},status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)


class DraftPostssAccView(generics.ListAPIView):
    permission_classes = [AllowAny,]
    queryset = DraftPosts.objects.all()
    serializer_class = DraftPostsAccGeneralSerializer
    pagination_class = ArticlesStatsPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'meta',
                     'slug', ]

    def get_queryset(self):
        user = self.request.query_params.get('user')
        test = get_object_or_404(User, unique_id=user)
        try:
            return DraftPosts.objects.filter(user__unique_id=user).order_by('-date')
        except Exception:
            return []
        # try:
        #     if str(self.request.user) != user:
        #         raise ValidationError(status.HTTP_401_UNAUTHORIZED)
        #     if test := DraftPosts.objects.filter(user__unique_id=user).exists():
        #         return DraftPosts.objects.filter(user__unique_id=user).order_by('-date')
        #     return []
        # except:
        #     return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "user": self.request.query_params.get('user'),
            }
        )
        return context


class DraftPostsDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        user = request.data.get('user', None)
        if request.user.is_active:
            try:
                test = DraftPosts.objects.filter(slug=slug).exists()
                if test:
                    if request.user.id == user:

                        post = DraftPosts.objects.filter(slug=slug)
                        post.delete()
                        return Response({"message": "DraftPosts Deleted"}, status=status.HTTP_200_OK)
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)


class DraftPostsEditDetail(APIView):
    permission_classes = []
    authentication_classes = []
    # queryset = DraftPosts.objects.all()
    serializer_class = DraftPostsEditDetailSerializer

    def get(self, request, *args, **kwargs):
        slug = self.request.query_params.get('slug')
        print(slug)
        # user = self.request.headers.get('Authorization')
        # user1 = RefreshToken(user)
        # print(user1['user_id'])
        # user1=User.objects.get(username=user)
        # print(user1)
        # print(user1.id)
        # test = get_object_or_404(DraftPosts, slug=slug)
        try:
            queryset = DraftPosts.objects.get(
                slug=slug)
            data = {
                "id": queryset.id,
                "title": queryset.title,
                "meta": queryset.meta,
                "description": queryset.description,
                "category": queryset.category,
                "read_min": queryset.category,
                "user": queryset.user.unique_id
            }
            print("user->>", data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DraftPostsSingleGetView(generics.ListAPIView):
    serializer_class = DraftPostsGetSerializer
    queryset = DraftPosts.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        post = self.request.query_params.get('post')
        if not (test := DraftPosts.objects.filter(slug=post).exists()):
            raise ValidationError("Post not found.")
        else:
            return DraftPosts.objects.filter(slug=post)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "post": self.request.query_params.get('post'),
            }
        )
        return context


class DraftPostsUpdateView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny,]
    # authentication_classes = []

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        print(slug)
        title = request.data.get('title', None)
        print(title)
        user = request.data.get('user', None)
        print(user)
        meta = request.data.get('meta', None)
        print(meta)
        description = request.data.get('description', None)
        print(description)
        category = request.data.get('category', None)
        print(category)
        test1 = json.loads(description)
        size = asizeof.asizeof(test1)/1024
        if size < 1000:

            if title is None or slug is None or meta is None or description is None:
                return Response({"message": "There should be a slug/title/meta/description of the post."}, status=status.HTTP_400_BAD_REQUEST)
            if slug is not None and title is not None and meta is not None and description is not None and user is not None:

                if DraftPosts.objects.filter(user__unique_id=user, slug=slug).exists():
                    print("in")
                    post = DraftPosts.objects.get(
                        user__unique_id=user, slug=slug)
                    print(post)
                    user1 = User.objects.get(unique_id=user)
                    if user1 is not None:
                        if user1.is_active:
                            try:
                                post.user = user1
                                post.title = title
                                post.meta = meta
                                post.description = description
                                post.category = category.split(',')
                                post.save()
                                print("done")
                                return Response({"message": "DraftPosts Updated"}, status=status.HTTP_200_OK)
                            except Exception:
                                return Response(status=status.HTTP_400_BAD_REQUEST)
                        return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({"message": "No User found."}, status=status.HTTP_401_UNAUTHORIZED)

                return Response({"message": "No DraftPosts found."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)


def delete_DraftPosts(slug):
    DraftPosts = DraftPosts.objects.filter(slug=slug)
    if DraftPosts:
        DraftPosts.delete()
        return True
    else:
        return False


class DraftPostsPublishView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        DraftPosts_slug = request.data.get("DraftPosts_slug", None)
        title = request.data.get('title', None)
        user = request.data.get('user', None)
        meta = request.data.get('meta', None)
        description = request.data.get('description', None)
        test1 = json.loads(description)
        size = asizeof.asizeof(test1)/1024
        if size < 1000:
            # check = None
            # for inx, obj in enumerate(test1['blocks']):
            #     if obj['type'] == "image":
            #         response = requests.get(obj['data']['url'])
            #         try:
            #             with concurrent.futures.ThreadPoolExecutor() as executor:
            #                 future = executor.submit(
            #                     NudityDetect, response.content)
            #                 return_value = future.result()
            #                 if return_value == False:
            #                     check = False
            #                 if return_value == True:
            #                     check = True
            #         except:
            #             check = False
            # print("check-->", check)
            # if check == True or check == None:
            if title is None or meta is None or description is None:
                return Response({"message": "There should be title/meta/description of the post."}, status=status.HTTP_400_BAD_REQUEST)
            if title is not None and meta is not None and description is not None and user is not None:
                try:
                    post = Posts()
                    user1 = User.objects.get(unique_id=user)
                    test_image = firstImage(description)
                    if user1 is not None:
                        if user1.is_active:
                            if test_image is not None:
                                DraftPosts_test = delete_DraftPosts(
                                    DraftPosts_slug)
                                if DraftPosts_test:
                                    post.user = user1
                                    post.title = title
                                    post.meta = meta
                                    post.have_image = True
                                    post.description = description
                                    post.save()
                                    return Response({"message": "Post Created"}, status=status.HTTP_200_OK)
                                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                DraftPosts_test = delete_DraftPosts(
                                    DraftPosts_slug)
                                if DraftPosts_test:
                                    post.user = user1
                                    post.title = title
                                    post.meta = meta
                                    post.description = description
                                    post.save()
                                    return Response({"message": "Post Created"}, status=status.HTTP_200_OK)
                                return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
                        return Response({"message": "Your Account Is Suspended."}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "Story Detail exceeds max size limit.", "size": round(size/1024, 2)}, status=status.HTTP_403_FORBIDDEN)
