$(function () {

    function refresh(html) {
        $('#table_area').html(html);
        $('ul.pager a').on('click', function () {
            let activity_configs = $('#query_form').serializeForm();
            let action = $(this).attr('action');
            console.log(action);
            activity_configs.page = changePage(action);
            query(activity_configs);
        });
    }

    function query(data) {
        $.get('/mana_app/activity/statistics/query/', data, function (resp) {
            if (resp.success) {
                refresh(resp.html);
                toptips(resp.msg, 'success');
            } else {
                toptips(resp.msg, 'danger');
            }
        });
    }

    $('#query_btn').on('click', function () {
        let form = $('#query_form');
        if (!form.valid()) return false;
        let data = form.serializeForm();
        let page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length === 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        query(data);
    }).trigger('click');

    $('#gen_excel_btn').on('click', function () {
        let form = $('#query_form');
        if (!form.valid()) return false;
        let data = form.serializeForm();
        data['mode'] = 'excel';
        let query_string = toQueryString(data);
        window.open('/mana_app/activity/statistics/query/' + query_string);
    });

});
