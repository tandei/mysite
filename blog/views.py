from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Count

from .models import Blog, BlogType
from datetime import datetime
from read_statistics.models import ReadNum
from read_statistics.utils import read_statistics_once_read
#from user.forms import LoginForm
#from comment.models import Comment
#from comment.forms import CommentForm

# 设置分页数量
EACH_PAGE_BLOG_NUMBER = settings.EACH_PAGE_BLOG_NUMBER

def get_blog_list_common_date(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, EACH_PAGE_BLOG_NUMBER)
    page_num = request.GET.get('page', 1) #获取页码参数(GET)
    page_of_blogs = paginator.get_page(page_num)
    current_rang_num = page_of_blogs.number #获取当前页码

    page_range = [x for x in range(current_rang_num-2,current_rang_num+3) if 0 < x <= paginator.num_pages]  #仅显示当前页前后几页

    #省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0,'...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    #首尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取博客分类对应博客数量
    blog_types_list = BlogType.objects.annotate(blog_count=Count('blog_blog')) #实际解析为sql，使用时执行
    '''blog_types = BlogType.objects.all() #循环，写入内存，增加服务器负担
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''

    #获取日期归档对应的博客数量
    '''blog_dates = Blog.objects.dates('create_time', 'month', order="DESC") \
                                 .annotate(blog_count=Count('create_time'))
                blog_dates_dict = {}
                for blog_date in blog_dates_dict[::2]'''
    blog_dates = Blog.objects.dates('create_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, 
                            create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = blog_types_list
    # context['blog_dates'] = Blog.objects.dates('create_time', 'month', order="DESC")
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_date(request, blogs_all_list)
    # context['blogs_count'] = Blog.objects.all().count()
    #return render_to_response("blog/blog_list.html", context)
    return render(request, "blog/blog_list.html", context)

def blog_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    blogs_all_list = Blog.objects.filter(blog_type__id=blog_type_pk)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = blog_type
    #return render_to_response("blog/blog_with_type.html", context)
    return render(request, "blog/blog_with_type.html", context)

def blog_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_with_date'] = '%s年%s月' % (year, month)
    #return render_to_response("blog/blog_with_date.html", context)
    return render(request, "blog/blog_with_date.html", context)

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    #blog_content_type = ContentType.objects.get_for_model(blog)
    #comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None)

    context = {}
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    #context['comments'] = comments.order_by('-comment_time')
    # 评论数
    #context['comment_count'] = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk).count()
    #context['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model, 'object_id': blog_pk, 'reply_comment_id': 0})
    response = render(request, 'blog/blog_detail.html', context) #响应
    # 过期时间expirse=datetime
    response.set_cookie(read_cookie_key, 'true', max_age=60) #阅读cookie标记
    return response
