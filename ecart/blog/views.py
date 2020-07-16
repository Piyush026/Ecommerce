from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import BlogPost


# Create your views here.

def index(request):
    allprods = []
    blog = BlogPost.objects.all()
    print(blog)
    # for x, y in catprods:
    #     allprods.append(x.object_id)
    #     allprods.append(y.title)
    return render(request, 'blog/index.html', {"blog": blog})


def blogPost(request, id):
    post = BlogPost.objects.filter(blog_id=id)[0]
    print(post)
    return render(request, 'blog/blogPost.html', {"post": post})
