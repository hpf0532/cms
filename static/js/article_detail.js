$("#div_digg .action").click(function () {
    if ($("#info").attr("username")) {
        var isUp = $(this).hasClass("diggit");
        var articleId = $("#info").attr("article_id");

        $.ajax({
            url: "/blog/up_down/",
            type: "post",
            data: {
                is_up: isUp,
                article_id: articleId
            },
            success: function (data) {
                console.log(data);
                if (data.state) {//赞或者灭成功
                    if (isUp) {
                        var num = $("#digg_count").text();
                        num = parseInt(num) + 1;
                        $("#digg_count").text(num);
                    } else {
                        var num = $("#bury_count").text();
                        num = parseInt(num) + 1;
                        $("#bury_count").text(num);
                    }
                } else { // 重复提交
                    if (data.first_action) {
                        $("#digg_tips").html("您已经赞过了");
                    } else {
                        $("#digg_tips").html("您已经踩过了");
                    }

                    setTimeout(function () {
                        $("#digg_tips").html("");
                    }, 5000)
                }
            }
        })
    }else{
        location.href = "/login/";
    }

});
