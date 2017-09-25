/**
 * Created by wyf on 2017/9/19.
 */
//注册模态框内注册按钮触发事件
$("#register-btn").click(function () {
    $(".register-form .form-group .error").remove();
    $.ajax({
        url:"/register/",
        type:"POST",
        headers:{"X-CSRFToken": $.cookie('csrftoken')},
        data:$(".register-form").serialize(),
        dataType:'JSON',
        success:function (arg) {
            console.log(arg);
            if(arg.status){
                $("#RegisterModal").modal('hide');
                alert("Register Successed!");
                // location.href = "/index/";
            }else{
                console.log(arg.msg);
            /*
            arg.msg = {
                email: ['xxxxx',]
                password: ['xxxxx',]
                user: ['xxxxx',]
            }
             */
            $.each(arg.msg,function (k,v) {

                var tag = document.createElement('span');
                tag.innerHTML = v[0];
                tag.className = "error";
                tag.style = "color:deepskyblue;position:absolute;left:25%;top:35px";
                // console.log(tag);
                // <span class='error'>v[0]</span>
                //$('#login_btn').before(tag);
                $('.register-form .form-group input[name="'+k+'"]').after(tag);
            })
        }
        }
    });
});
//登录模态框内登录按钮触发事件
$("#login-btn").click(function () {
    $(".login-form .form-group .error").remove();
    $.ajax({
        url:"/login/",
        type:"POST",
        headers:{"X-CSRFToken": $.cookie('csrftoken')},
        data:$(".login-form").serialize(),
        dataType:'JSON',
        success:function (arg) {
            console.log(arg);
            if(arg.status){
                $("#LoginModal").modal('hide');
                alert("Login Successed!");
                location.href = "/index/";
            }else{
                console.log(arg.msg);
            /*
            arg.msg = {
                email: ['xxxxx',]
                password: ['xxxxx',]
                user: ['xxxxx',]
            }
             */
            $.each(arg.msg,function (k,v) {
                var tag = document.createElement('span');
                tag.innerHTML = v[0];
                tag.className = "error";
                tag.style = "color:red;position:absolute;left:25%;top:35px";
                // console.log(tag);
                // <span class='error'>v[0]</span>
                //$('#login_btn').before(tag);
                $('.login-form .form-group input[name="'+k+'"]').after(tag);
            })
        }
        }
    });
});

// url-tag失去焦点自动获取title和description事件
$("#url-tag").blur(function () {
    $(".publish-form .form-group .error").remove();
    var $get_url = $(this).val();
    console.log($get_url);
    $.ajax({
       url:"/publish/",
       type:"GET",
       // headers:{"X-CSRFToken": $.cookie('csrftoken')},
       data:{'get_url':$get_url},
       dataType:'JSON',
       success:function (arg) {
           console.log(arg);
           $("#title-tag").val(arg.title);
           $("#summary-tag").val(arg.desc);
       }
       
   }) 
});

//上传图片事件
$(".send-img-btn").click(function(){
    $(".publish-form .form-group .error").remove();
    // 获取文件
    // 上传文件
    // 预览
    var img_data = new FormData();  // new一个容器对象(变量)，用来存放文件
    img_data.append('img_data',$('#picture-tag')[0].files[0]); //将文件存放到变量中
    console.log(img_data);
    $.ajax({
        url: '/upload_img/',
        type: 'POST',
        headers:{"X-CSRFToken": $.cookie('csrftoken')},
        data: img_data,
        processData: false,  // tell jQuery not to process the data 不改变img_data的数据格式
        contentType: false,  // tell jQuery not to set contentType
        success:function (arg) {
            arg = JSON.parse(arg);
            if (arg.status){
                var tag = document.createElement('img'); //新建img标签，用来预览图片
                tag.src = "/" + arg.path; //加入刚上传的图片路径
                tag.style = "max-width:100%"; //设置样式
                $('#img-container').empty(); //先清空img容器标签
                $('#img-container').append(tag); //再加入img容器标签
                $('#avatar-tag').val("\\" + arg.path); //将图片路径加到隐藏的input框(form提交会提交这个路径)
            }else{
                $('#img-container').text('没有正确获取到图片！')
            }
        }
    })
});

//发布按钮事件
$("#publish-btn").click(function () {
    $(".publish-form .form-group .error").remove();
    $.ajax({
        url:"/publish/",
        type:"POST",
        headers:{"X-CSRFToken": $.cookie('csrftoken')},
        data:$(".publish-form").serialize(),
        dataType:'JSON',
        success:function (arg) {
            console.log(arg);
            if(arg.status){
                $("#PublishModal").modal('hide');
                alert("Publish Successed!");
                location.href = "/index/";
            }else{
                console.log(arg.msg);
            /*
            arg.msg = {
                email: ['xxxxx',]
                password: ['xxxxx',]
                user: ['xxxxx',]
            }
             */
            $.each(arg.msg,function (k,v) {

                var tag = document.createElement('span');
                tag.innerHTML = v[0];
                tag.className = "error";
                tag.style = "color:deepskyblue;position:absolute;left:5%;top:35px";
                // console.log(tag);
                // <span class='error'>v[0]</span>
                //$('#login_btn').before(tag);
                $('.publish-form .form-group input[name="'+k+'"],.publish-form .form-group textarea[name="'+k+'"]').after(tag);
            })
        }
        }
    });
});

//点赞按钮触发事件
$("#content-list").on("click",".digg-a",function () {
    if($('.action-nav a[href="/logout/"]').length){ //判断是否存在注销标签
        // alert("点了个赞！");
        var new_id = $(this).parent().attr("newid");
        var digg_count = $(this).children("b").text(); //当前显示点赞数
        // console.log(new_id);
        // console.log(digg_count);
        $.ajax({
            url:"/digg/",
            type:"POST",
            headers:{"X-CSRFToken": $.cookie('csrftoken')},
            data:{"new_id":new_id},
            dataType:"JSON",
            success:function (arg){
                if(arg.status){
                    // 前端点赞自加1
                    $('.part2[newid="'+ new_id +'"] .digg-a b').text(parseInt(digg_count)+1);
                    // location.href = "/index/";
                }else{
                    alert('你已经点过赞了！')
                }
            }
        })
    }
    else{ //不存在logout标签则弹出登录对话框
        $("#LoginModal").modal('show');
    }
});