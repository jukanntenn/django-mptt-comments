# django-mptt-comments

拓展 django 官方的评论库，为评论提供无限层级的支持。

## 安装


安装 django-mptt-comments:

    pip install django-mptt-comments

将应用及其依赖添加到 `INSTALLED_APPS`:

    INSTALLED_APPS = (
        ...
        'django.contrib.sites',
        'django_comments',
        'django_mptt_comments',
        'captcha',
        'mptt',
        ...
    )
    
添加必要的 settings 设置：

    MPTT_COMMENTS_ALLOW_ANONYMOUS = True # True 为允许匿名评论，否则不允许
    COMMENTS_APP = 'django_mptt_comments'
    SITE_ID = 1

添加应用的 URL:

    urlpatterns = [
        ...
        url(r'mpttcomments', include('django_mptt_comments.urls')),
        url(r'captcha', include('captcha.urls')),
        ...
    ]

因为应用在视图函数外引用了 request，因此需要添加一个中间件支持，并且推荐添加到所有中间件列表的最后：


    MIDDLEWARE = [
        ...
        'crequest.middleware.CrequestMiddleware',
    ]
    
设置数据库（一定先备份原数据库！！！）

    python manage.py migrate

## 渲染评论表单

为了能够让用户发表评论，我们需要在适当的地方为用户提供一个评论表单，添加表单的方法很简单，打开模板文件，引入模板标签，渲染模板即可。

举个例子，你想为你的某一篇博客文章添加评论表单，假设在模板中，表示博客文章的模板变量为 `post`，那么，可以这样为博客文章渲染一个评论表单：

    {% load mptt_comment_tags %}
    {% render_mptt_comment_form for post %}

这将渲染 comments/form.html 页面，所以如果你想自定义渲染的表单样式，可以在你的项目的模板目录路径下新增一个 comments/form.html，参考默认模板的内容，按需修改即可。

## 渲染回复列表

展示某个对象下的全部评论，也可以使用模板标签来完成，例如需要显示博客文章 post 下的全部评论，只需要：

    {% load comments %}
    {% render_comment_list for post %}
    
这将渲染 comments/list.html 页面，所以同样可以自定义渲染样式，方法和渲染表单类似。

## 运行 example 工程
1. 克隆项目到本地
2. 进入 example 文件夹
3. 【可选，推荐】创建虚拟环境
4. 安装依赖
5. 创建数据库
6. 导入数据
7. 运行 manage.py runserver
8. 访问 127.0.0.1:8000
