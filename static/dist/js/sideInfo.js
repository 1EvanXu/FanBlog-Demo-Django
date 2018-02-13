$(
    function () {
        getLatestArticles();
        getPopularArticles();
        getCategories();
    }


);

    function getLatestArticles() {
        $.ajax({
            url: "/blog/side/latest/",
            type: "GET",
            dataType: 'json',
            success: function (list) {
                showLatestArticlesList(list);
            },
            complete: function () {
                $("#latest-articles-box").children("div.overlay").remove();
            }
        })
    }

    function showLatestArticlesList(list) {
        var ulList = $("#latest-articles-box").children("div.box-body").children("ul.list-unstyled");
        for (var i in list) {
            ulList.append("<li><a href='" + list[i].link + "'>" + list[i].title + "</a></li>");
        }
    }

    function getPopularArticles() {
        $.ajax({
            url: "/blog/side/popular/",
            type: "GET",
            dataType: "json",
            success: function (list) {
                showPopularArticles(list);
            },
            complete: function () {
                $("#popular-articles-box").children("div.overlay").remove();
            }
        });
    }

    function showPopularArticles(list) {
        var ulList = $("#popular-articles-box").children("div.box-body").children("ul.list-unstyled");
        for (var i in list) {
            ulList.append("<li><a href='" + list[i].link + "'>" + list[i].title + "</a>" +
                "<span class='pull-right text-gray'>" + list[i].popularity + "</span></li>");
        }
    }

    function getCategories() {
        $.ajax({
            url: "/blog/side/categories/",
            type: "GET",
            dataType: "json",
            success: function (list) {
                showCategories(list);
            },
            complete: function () {
                $("#category-box").children("div.overlay").remove();
            }
        })
    }

    function showCategories(list) {
        var ulList = $("#category-box").children("div.box-body").children("ul.list-unstyled");
        for (var i in list) {
            var li = "<li><a href='/blog/categories/" + list[i].categoryId + "/'>" + list[i].categoryName +
                "</a><span class='pull-right text-gray'>" + list[i].ownArticles + "</span></li>";
            ulList.append(li);
        }
    }

