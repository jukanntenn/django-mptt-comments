# django-mptt-comments


## 安装


安装 django-mptt-comments:

    pip install django-mptt-comments

将应用添加到 `INSTALLED_APPS`:

    INSTALLED_APPS = (
        ...
        'django_comments',
        'django_mptt_comments',
        ...
    )

添加应用的 URL:

    from django_mptt_comments import urls as django_mptt_comments_urls


    urlpatterns = [
        ...
        url(r'^', include(django_mptt_comments_urls)),
        ...
    ]

因为应用在视图函数外引用了 request，因此需要添加一个中间件支持，并且推荐添加到所有中间件列表的最后：


    MIDDLEWARE = [
        ...
        'crequest.middleware.CrequestMiddleware',
    ]

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
