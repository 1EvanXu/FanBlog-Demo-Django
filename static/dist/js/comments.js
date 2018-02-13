
    $("#praise").click(function () {
        var cls = $("#praise-logo").attr("class");
        if (cls == "fa fa-thumbs-up"){
                return false;
        }

        var n = $("#praise-number").html();
        n = parseInt(n);
        var sendData = {
            'pub_id': $("#pubId").text()
        };
        $.get('/blog/a/praise/', sendData, function (r) {

            if (r == "False")
                return false;

            cls = "fa fa-thumbs-up";
            $("#praise-logo").attr("class", cls).html("已赞");
            $("#praise-number").html(n+1);
        });

    });

    $("#submit-comment").click(function () {
        var comment = $("#comment-content").val();
        console.log(comment);
        if (comment.length >= 302) {
            alert("评论最多300字!");
            return;
        }

        if (comment.length == 0) {
            alert("评论不能为空");
            return;
        }



        var data = {
            'pub_id': $("#pubId").text(),
            'comment': comment
        };

        var sp = $("#comment-content-label").children('span');
        if (sp.length != 0) {
            data['commentIdReply'] = new String(sp.html()).split(":")[0];
            data['childCommentIdReply'] = new String(sp.html()).split(":")[1];
        }

        console.log(data);

        $("#comment-textarea").append("<div class='overlay'><i class='fa fa-spinner fa-spin'></i></div>");
        $("#comment-content").attr("disabled", "disabled");
        $("#submit-comment").attr("disabled", "disabled");
        var targetUrl = "/blog/a/comment/";

        $.ajax({
            url: targetUrl,
            type: "POST",
            dataType: "text",
            data: data,
            success: function (r) {
                $("#submit-result").html(r);
                setTimeout(function () {
                   $("#submit-result").html("");
                }, 3000);

                $("#chat-box").empty();
                loadComment();

            },
            complete: function () {
                $("div.overlay").remove();
                $("#comment-content").removeAttr("disabled");
                $("#submit-comment").removeAttr("disabled");
            }
        })
    });

    $(loadComment());

    function loadComment() {
        $.ajax({
           url: '/blog/a/load_comments',
           type: 'GET',
           dataType: 'json',
           data: {'pub_id': $("#pubId").text()},
           success: function (r) {
                for(var i = 0; i <  r.length; i++) {
                    generateComment(r[i]);
                }
           },
           error: function () {

           }
        });
    }

    function generateComment(c) {

        var itemId = "comment-" + c.commentId;
        $("#chat-box").append("<div id=\"" + itemId +"\" class=\"item\"><img src=\"/static/dist/img/user-default.jpg\" alt=\"user image\">" +
            "<p class=\"message\"><a class=\"name\"><small class=\"text-muted pull-right\"><i class=\"fa fa-clock-o\"></i>" +
            c.commentTime + "</small><span>"+ c.commentator +"</span></a>" + c.commentContent + "</p><div class=\"pull-right\">"
                + "<br><a name=\"reply\" href=\"#comment-area\" class=\"btn btn-default btn-xs\" onclick=\"toReply(this)\">回复</a></div></div><hr>"
        );

        var childComments = c.childComments;

        if(childComments != undefined) {
            itemId = "#" + itemId;
            for(var i = 0; i < childComments.length; i++){
                var childComment = childComments[i];
                var replyer = "<a>" + childComment.commentator + "</a>";
                if (childComment.replyTo != undefined) {
                    replyer = replyer + "回复<a>" + childComment.replyTo + "</a>";
                }
                $(itemId).children('div.pull-right').before("<div id=\"childComment-" + childComment.commentId +
                    "\" class=\"attachment\"><h4>" + replyer + "</h4><p><small class=\"pull-right\">" +
                    childComment.commentTime + "</small>" + childComment.commentContent  +
                    "</p><div class=\"pull-right\"><a name=\"child-reply\" href=\"#comment-area\" " +
                    "style=\"font-size: 10px\" onclick=\"toReply(this)\">回复</a></div></div>"
                );
            }
        }
    }

    function toReply(a) {

        var name = a.name;
        var replyer;
        var childCommentId = "";
        var commentId = "";
        if (name == "child-reply") {
            var obj1 = $(a).parent().prevAll('h4');
            replyer = $(obj1.children()[0]).html();
            console.log("child-reply",replyer);
            childCommentId = obj1.parent().attr('id');
            childCommentId = new String(childCommentId).split("-")[1];
            commentId = obj1.parent().parent().attr('id');
            commentId = new String(commentId).split('-')[1];
        } else if(name == "reply") {
            var obj2 = $(a).parent().parent().children('p').children('a');
            replyer = obj2.children('span').html();
            console.log("reply", replyer);
            commentId = $(a).parent().parent().attr('id');
            commentId = new String(commentId).split('-')[1];
        }

        console.log(commentId,":", childCommentId);

        $("#comment-content-label").removeAttr('hidden').html("回复" + replyer + ":" +
            "<span hidden=\"hidden\">" + commentId + ":" + childCommentId +"</span>");

    }
