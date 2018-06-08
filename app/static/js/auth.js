// 验证邮箱格式
function validateEmail(email) {
    var re = /^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$/;
    return re.test(email.toLowerCase());
}

// 验证码倒计时
var count = 60;
function countdown(obj) {
    if (count == 0) {
        obj.attr('disabled',false);
        obj.html("获取验证码");
        count = 60;
        obj.next().html(" ");
        return;
    } else {
        obj.attr('disabled',true);
        obj.html(count + " 秒后重新发送");
        count--;
    }
    setTimeout(function() {
        countdown(obj) }
        ,1000)
}

// ready
$(function () {
    // 获取标签
    var t = $('#t'),
        name = $('#name'),
        email = $('#email'),
        email2 = $('#email2'),
        csrf = $('#csrf'),
        pwd = $('#pwd'),
        auth_code = $('#auth_code'),
        send_auth_code = $('#send_auth_code'),

        name_error = true,
        pwd_error = true,
        email_error = true,
        auth_code_error = true;

    // 失去焦点判断
    auth_code.blur(function () {
        check_auth_code();
    });
    name.blur(function () {
        check_name();
    });
    pwd.blur(function () {
        check_pwd();
    });
    email.blur(function () {
        check_email();
    });

    //  检查函数
    function check_name() {
        if (name.val().trim().length > 2 && name.val().trim().length < 20) {
            name_error = false;
            name.prev().hide();
        } else {
            name_error = true;
            name.prev().html('用户名长度必须大于2并且小于20').show();
        }
    }
    function check_pwd() {
        if (pwd.val().length < 6) {
            pwd_error  = true;
            pwd.prev().html('密码长度最少6位').show();
        } else {
            pwd_error = false;
            pwd.prev().hide();
        }

    }
    function check_email() {
        if (validateEmail(email.val().trim())) {
            email_error = false;
            email.prev().hide();
        } else {
            email_error = true;
            email.prev().html('邮箱格式错误').show();
        }
    }
    function check_auth_code() {
        if (auth_code.val().length != 6) {
            auth_code_error = true;
            auth_code.prev().html('验证码错误').show();
        } else {
            auth_code_error = false;
            auth_code.prev().hide();
        }
    }

    // 获取验证码
    send_auth_code.click(function (event) {
        event.preventDefault();
        check_email();

        if (!email_error) {
            countdown(send_auth_code);
            send_auth_code.next().html("验证码已发送至您的邮箱,请注意查收. 验证码5分钟后过期");
            $.post('/auth/send_auth_code', {'email': email.val(), 'csrf_token': csrf.val()}, function (data) {
                t.val(data.t);
                email2.val(data.email2);
            });
        }
    });

    // register
    $('#register_form').submit(function (event) {
        // 阻止表单默认提交
        event.preventDefault();

        // 调用检查函数
        check_pwd();
        check_name();
        check_email();
        check_auth_code();

        // 验证全部通过才会继续执行
        if (!name_error && !pwd_error && !email_error && !auth_code_error) {
            var data = {
                't': t.val(),
                'csrf_token': csrf.val(),
                'name': name.val().trim(),
                'email': email.val().trim(),
                'email2': email2.val().trim(),
                'auth_code': auth_code.val(),
                // sha1加密
                'pwd': CryptoJS.SHA1(pwd.val()).toString()
            };

            $.post('/auth/register', data, function (data) {
                // 根据返回的error 对用户进行响应

                switch (data.error) {
                    case 'name_error':
                        name.prev().html(data.reason).show();
                        break;
                    case 'email_error':
                        email.prev().html(data.reason).show();
                        break;
                    case 'email2_error':
                        email.prev().html(data.reason).show();
                        break;
                    case 'auth_code_error':
                        auth_code.prev().html(data.reason).show();
                        break;

                    // 全部通过转到主页
                    default :
                        location.assign('/')
                }

            });
        }
    });

    // login
    $('#login_form').submit(function (event) {
        event.preventDefault();

        check_pwd();
        check_email();

        if (!pwd_error && !email_error) {
            var data = {
                'csrf_token': csrf.val(),
                'email': email.val().trim(),
                'pwd': CryptoJS.SHA1(pwd.val()).toString()
            };

            $.post('/auth/login', data, function (data) {
                switch (data.error) {
                    case 'email_error':
                        email.prev().html(data.reason).show();
                        break;
                    case 'pwd_error':
                        pwd.prev().html(data.reason).show();
                        break;
                    default :
                        location.assign('/')
                }
            });

        }
    });


});



