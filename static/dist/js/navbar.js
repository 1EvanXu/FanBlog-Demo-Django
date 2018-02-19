$(function () {
    getNavBarInfo();
});

function getNavBarInfo() {

    var target = '/back/statistics/nav/';
    $.get(target, function(r){
        $("#administrator").html("&nbsp;" + r.admin);
        $("#admin-sidebar").html(r.admin);
        $("#admin-sidebar-img").attr("src", r.adminImg);
        var tasksMenu = $("#tasks-menu");
        tasksMenu.children('a').children('span').html(r.uncompleted);
        var tasksDropDownMenu = tasksMenu.children('ul.dropdown-menu');
        var tasksDropDownMenuBody = tasksDropDownMenu.children('li.body');
        var tasksDropDownMenuHeader = "您还有" + r.uncompleted + "篇文章未完成。";
        var tasksProgress = $("#tasks-progress");
        if (r.uncompleted = 0) {
            tasksDropDownMenuHeader = '没有未完成的文章。';
            tasksDropDownMenuBody.remove();
            tasksDropDownMenu.children('li.footer').remove();

        }
        tasksDropDownMenu.children('li.header').html(tasksDropDownMenuHeader);
        tasksDropDownMenuBody.find('small.pull-right').html(r.percentage + '%');
        tasksProgress.css("width", r.percentage + "%");
        tasksProgress.children('span').html(r.percentage + "completed");

        var messageMenu = $("#messages-menu");
        var messageCountLabel = messageMenu.children('a.dropdown-toggle').children('span');
        var messageDropdownMenu = messageMenu.children('ul.dropdown-menu');
        messageCountLabel.html(r.unreadMsgNum);
        messageDropdownMenu.empty();
        if (r.unreadMsgNum === 0){
            messageDropdownMenu.html("<li class=\"header\">" + "没有新的留言" + "</li>");
        } else {
            messageDropdownMenu.html("<li class=\"header\">您还有" + r.unreadMsgNum + "条留言未读</li>" +
                "<li class=\"footer\"><a href=\"/back/message/\">查看所有留言>></a></li>");
        }
    })
}