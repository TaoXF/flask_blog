import time
from datetime import datetime
from manage import app


# 格式化时间戳
@app.template_filter('datetime')
def datetime_filter(t):
    delta = int(time.time() - float(t))
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


# jinja2 切片 filter
@app.template_filter('slice')
def slice_filter(content, start, end):
    return content[start: end]


# jinja2 markdown 渲染
@app.template_filter('md')
def markdown_filter(txt):
    from markdown import markdown
    return markdown(txt)