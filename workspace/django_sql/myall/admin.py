from django.contrib import admin
from myall.models import Blog, Tag, BlogTag, MBlog, MTag

class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('blog', 'tag')


admin.site.register(Blog)
admin.site.register(Tag)
admin.site.register(MBlog)
admin.site.register(MTag)
admin.site.register(BlogTag, BlogTagAdmin)
