from django.contrib import admin
from .models import (Posts, TrendingPosts,
                     DraftPosts, SuspendedPost, IsPrimary,
                     IsSecondary, CategoryPosts, ReadMinutesOfPosts)

# Register your models here.


class PostAdminConfig(admin.ModelAdmin):
    model = Posts
    search_fields = ('title', 'meta', 'slug',)
    list_filter = ('date',)
    ordering = ('-date',)
    list_display = ('slug', 'have_image',
                    'date',)


admin.site.register(Posts, PostAdminConfig)
admin.site.register(DraftPosts)
admin.site.register(SuspendedPost)
admin.site.register(IsPrimary)
admin.site.register(IsSecondary)
admin.site.register(TrendingPosts)
admin.site.register(CategoryPosts)
admin.site.register(ReadMinutesOfPosts)
