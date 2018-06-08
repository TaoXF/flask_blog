// 路径导航
function create_breadcrumb(name) {
    var result;

    result = '<ol class="breadcrumb">';
    result += '<li><a href="/">首 页</a></li>';
    result += '<li class="active">' + name + '</li></ol>';

    return result;
}
// 列表页文章
function create_one_article(article) {
    var result;

    result = '<article class="article">';
    result += '<h1><a data-article href="/article/' + article.id + '">' + article.title + '</a></h1>';
    result += '<div class="summary">' + article.summary + '</div>';
    result += '<div class="article-meta">';
    result += '<a data-article-list href="/classify/' + article.classify.id + '/article_list"';
    result += 'class="article-classify">' + article.classify.title + '</a>';
    result += '<span> / </span>';
    result += '<ul class="article-tags">';

    article.tags_list.forEach(function (tags) {
        result += '<li><a data-article-list href="/tags/' + tags.id + '/article_list">' + tags.title + '</a></li>';
    });

    result += '</ul>';
    result += '<span> / </span>';
    result += '<time>' + article.create_at + '</time>';
    result += '</div>';
    result += '<div class="article-button">';
    result += '<a data-article href="/article/' + article.id + '">阅读全文 >></a>';
    result += '</div>';
    result += '</article>';

    return result;
}
// 文章分页
function create_pagination(pagination, model_name, model_id) {
    var result;

    result = '<nav id="pager" aria-label="Page navigation">';
    result += '<ul class="pagination">';

    if (pagination.has_prev) {
        // 上一页
        if (model_id) {
            result += '<li><a data-article-list href="' + '/' + model_name + '/' + model_id;
            result += '/article_list/' + Number(pagination.now_page - 1) + '">&laquo;</a></li>'
        } else {
            result += '<li><a data-article-list href="' + '/' + model_name;
            result += '/article_list/' + Number(pagination.now_page - 1) + '">&laquo;</a></li>'
        }
    } else {
        result += '<li class="disabled"><a href="javascript:">&laquo;</a></li>';
    }

    pagination.iter_pages.forEach(function (p) {
        if (p) {
            if (p === pagination.now_page) {
                // 当前页
                result += '<li class="active"><a href="javascript:">' + p + '</a></li>';
            } else {
                // 有id 就是外键查询 没id就是 所有文章查询
                if (model_id) {
                    result += '<li><a data-article-list href="' + '/' + model_name + '/' + model_id;
                    result += '/article_list/' + p + '">' + p + '</a></li>';
                } else {
                    result += '<li><a data-article-list href="' + '/' + model_name;
                    result += '/article_list/' + p + '">' + p + '</a></li>'
                }
            }
        } else {
            // 生成 ...
            result += '<li class="disabled"><a href="javascript:">&hellip;</a></li>';
        }
    });

    if (pagination.has_next) {
        // 下一页
        if (model_id) {
            result += '<li><a data-article-list href="' + '/' + model_name + '/' + model_id;
            result += '/article_list/' + Number(pagination.now_page + 1) + '">&raquo;</a></li>'
        } else {
            result += '<li><a data-article-list href="' + '/' + model_name;
            result += '/article_list/' + Number(pagination.now_page + 1) + '">&raquo;</a></li>'
        }
    } else {
        result += '<li class="disabled"><a href="javascript:">&raquo;</a></li>';
    }

    result += '</ul></nav>';

    return result;

}
// 请求文章列表页  更新页面
function init_article_list(event) {
    var loading = $('#loading');
    var main_wrap = $('#main-wrap');

    main_wrap.hide();
    loading.fadeIn();

    $.getJSON(event.attr('href'), function (data) {
        window.scrollTo(0,0);

        var result,
            article_list = '',
            pagination;

        data.articles.forEach(function (article) {
           article_list += create_one_article(article);
        });

        pagination = create_pagination(data.pagination, data.model_name, data.model_id);

        result = create_breadcrumb(data.model_name);
        result += article_list;
        result += pagination;

        loading.fadeOut();
        main_wrap.html(result).show();
    })

}


// ======================================================================================
// 生成文章页内容
function create_article_content(article) {
    var result;

    result = '<article id="article">';
    result += '<h2>' + article.title  + '</h2>';
    result += '<div class="article-meta">';
    result += '<a data-article-list class="article-classify" href="/classify/'+ article.classify.id;
    result += '/article_list">' + article.classify.title + '</a>';
    result += '<span> / </span><ul class="article-tags">';

    article.tags_list.forEach(function (tags) {
        result += '<li><a data-article-list href="/tags/' + tags.id + '/article_list">' + tags.title + '</a></li>';
    });

    result += '</ul><span> / </span><time>' + article.create_at + '</time></div>';
    result += '<div class="content">' + article.content + '</div></article>';
    result += '<div id="loading2"><img src="/static/images/loading.gif"></div>';
    result += '<div id="comment-wrap" data-id="' + article.id + '"></div>';

    return result;
}
// 文章页
function init_article(event) {
    var loading = $('#loading');
    var main_wrap = $('#main-wrap');

    main_wrap.hide();
    loading.fadeIn();

    $.getJSON(event.attr('href'), function (data) {
        // 回到顶部
        window.scrollTo(0,0);

        var result,
            article,
            comment;

        result = create_breadcrumb(data.article.title);
        result += create_article_content(data.article);

        main_wrap.html(result).show();
        loading.fadeOut();
    });
}


// ======================================================================================
// 所有留言
function create_comments(comment_list) {
    var result;

    result = '<ul>';

    comment_list.forEach(function (comment) {
         result += '<li><div class="img-wrap">';
         result += '<img src="' + comment.user.head_pic + '" class="img-responsive" alt="用户头像"></div>';
         result += '<div class="body"><div class="message-meta">';
         result += '<span>' + comment.user.name + '</span>';
         result += '<time>' + comment.create_at + '</time>';
         result += '<div class="message-content">' + comment.content + '</div>';
         result += '</div></li>';
    });

    result += '</ul>';

    return result
}
// 留言分页
function create_comment_pagition(pagination, article_id) {
    var result;

    result = '<nav id="pager" aria-label="Page navigation">';
    result += '<ul class="pagination">';

    if (pagination.has_prev) {
        result += '<li><a href="' + article_id + '/comments/' + Number(pagination.now_page - 1) + '">&laquo;</a></li>'
    } else {
        result += '<li class="disabled"><a href="javascript:">&laquo;</a></li>';
    }

    pagination.iter_pages.forEach(function (p) {
        if (p) {
            if (p === pagination.now_page) {
                result += '<li class="active"><a href="javascript:">' + p + '</a></li>';
            } else {
                result += '<li><a href="' + article_id + '/comments/' + p + '">' + p + '</a></li>'
            }
        } else {
            result += '<li class="disabled"><a href="javascript:">&hellip;</a></li>';
        }
    });

    if (pagination.has_next) {
        result += '<li><a href="' + article_id + '/comments/' + Number(pagination.now_page + 1) + '">&laquo;</a></li>'
    } else {
        result += '<li class="disabled"><a href="javascript:">&laquo;</a></li>';
    }

    result += '</ul></nav>';

    return result
}

// 留言输入框 验证是否登录
function create_input(is_authenticated, article_id, current_user_id) {
    var result;

    result = '<from>';
    result += '<textarea id="comment" style="resize:none" class="form-control" rows="5"';
    result += 'placeholder="来都来了, 不留下点什么吗？(>▽<)"></textarea>';

    if (is_authenticated) {
        result += '<input type="hidden" name="user_id" value="' + current_user_id + '">';
        result += '<input type="hidden" name="article_id" value="' + article_id + '">';
        result += '<button id="comment_btn" class="btn btn-default btn-xs">提交</button>';
        result += '<span class="error"> 留言不能为空,或超过200个字符</span>'
    } else {
        result += '<p>需要登录之后才能提交留言</p>'
    }

    result += '</from>';

    return result;
}

// 发请求 并创建留言面板
function init_comments(article_id) {
    var loading2 = $('#loading2');
    var url = '/' + article_id + '/comments';

    loading2.fadeIn();

    $.getJSON(url, function (data) {
        var result;


        result = '<h3>欢迎留言</h3>';
        result += '<div id="message_wrap">';
        if (data.has_comment) {
            result += create_comments(data.comment_list);
            if (data.pagination) {
                result += create_comment_pagition(data.pagination, article_id);
            }
        } else {
            result += '<p>还没有留言~ 赶紧抢个沙发吧 n(*≧▽≦*)n</p>';
        }

        result += '</div>';
        result += create_input(data.is_authenticated, article_id, data.current_user_id);

        $('#comment-wrap').html(result);
        loading2.fadeOut();
    });
}

// 用户提交留言
function post_comment() {
    var comment = $('#comment'),
        user_id = $('input[name="user_id"]').val(),
        article_id = $('input[name="article_id"]').val(),
        csrf_token = $('meta[_csrf]').attr('_csrf');

    var loading2 = $('#loading2'),
        message_wrap = $('#message_wrap');

    message_wrap.hide();
    loading2.fadeIn();

    if (comment.val().trim() && comment.val().trim().length < 200) {
        $('.error').hide();

        var url = '/' + article_id + '/comments',
            data = {
                'content': comment.val().trim(),
                'user_id': user_id,
                'article_id': article_id,
                'csrf_token': csrf_token
            };

        $.post(url, data, function (data) {

            comment.val('');

            var result;

            result = create_comments(data.comment_list);

            if (data.pagination) {
                result += create_comment_pagition(data.pagination, article_id);
            }

            loading2.fadeOut();
            message_wrap.html(result).show();

        }, "json");

    } else {
        $('.error').show();
    }
}


// ======================================================================================
// ready
$(function () {
    var main_wrap = $('#main-wrap');

    // 为第一次页面的a[data-article-list] 绑定事件
    $('a[data-article-list]').on('click', function (event) {
        event.preventDefault();
        init_article_list($(this));
    });

    // 为动态生成的a[data-article-list] 绑定事件 必须将事件 绑定在父级以上的元素才会生效
    main_wrap.on('click', 'a[data-article-list]', function (event) {
        event.preventDefault();
        init_article_list($(this));
    });

    // 文章内容页
    $('a[data-article]').on('click', function (event) {
        event.preventDefault();
        init_article($(this));
    });
    
    main_wrap.on('click', 'a[data-article]', function (event) {
        event.preventDefault();
        init_article($(this));
    });

    // 页面滚动到底部时加载 留言区
    $(window).scroll(function () {
        if ($(window).scrollTop() == $(document).height() - $(window).height()) {
            var comment_wrap = $('#comment-wrap');
            // 判断是否有comment_wrap
            if (comment_wrap.length > 0) {
                // 判断是否已经加载出留言区 避免无限加载
                if ($('#message_wrap').length == 0) {
                    init_comments(comment_wrap.attr('data-id'));
                }
            }
        }
    });

    // 提交留言
    main_wrap.on('click', '#comment_btn', function (evevt) {
        evevt.preventDefault();
        post_comment();

    });

    // 代码高亮
    $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
    });
});

