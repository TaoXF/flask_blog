$(function () {
    // checkbox 计数
    var checkbox = $('input[type="checkbox"]'),
        checkbox_count = $('#checkbox_count');

    checkbox.click(function () {
        checkbox_count.html($('input[type="checkbox"]:checked').length);
    });

    // 全选全消
    var is_check_all = false;
    $('#all_check').click(function () {
        if (is_check_all) {
            checkbox.each(function () {
                this.checked = false;
            });
            is_check_all = false;
            $('#all_check').html('全 选');
        } else {
            checkbox.each(function () {
                this.checked = true;
            });
            is_check_all = true;
            $('#all_check').html('全 消');
        }
        checkbox_count.html($('input[type="checkbox"]:checked').length);
    });

    var id_list = [],
        name_list= [];
    // 获取选中的model
    $('#delete_btn').click(function (event) {
        event.preventDefault();
        id_list = [];
        name_list = [];

        $('input[type="checkbox"]:checked').each(function () {
            id_list.push($(this).val());
            name_list.push(($(this).attr('name')));
        });
        var delete_models = $('.delete_models');

        delete_models.html('');
        name_list.forEach(function (elment) {
            var li = '<li>' + elment + '</li>';
            delete_models.append(li);
        });
    });

    $('#sure').click(function () {
        $.post('/admin/delete',
                {
                    'id_list': id_list.join(','),
                    'csrf_token': $('#csrf').attr('content'),
                    'model_name': $('#model_name').attr('content')
                },
            function () {
            // 刷新当前页
            window.location.reload();
        });
    });

});