from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import auth
from PIL import Image, ImageDraw, ImageFont
from cms.utils import aliyun
from io import BytesIO
from geetest import GeetestLib
from app01 import forms, models
from pytz import timezone
import random
import logging
import json

# 生成一个logger实例，专门用来记录日志
logger = logging.getLogger(__name__)

cst_tz = timezone('Asia/Shanghai')
# Create your views here.

# 登录视图
# def login(request):
#     if request.method == "POST":
#         print(request.POST)
#         # 初始化ret字典
#         ret = {"status":0, "msg": ""}
#
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         vaild_code = request.POST.get("vaild_code")
#
#         print(request.session.get("vaild_code"))
#         print("session存储的验证码".center(120, "="))
#         if vaild_code and vaild_code.upper() == request.session.get("vaild_code").upper():
#             user = auth.authenticate(username=username, password=password)
#             if user:
#                 auth.login(request, user)
#                 ret["msg"] = "/index/"
#             else:
#                 ret["status"] = 1
#                 ret["msg"] = "用户名或密码错误"
#         else:
#             ret["status"] = 1
#             ret["msg"] = "验证码错误"
#         return JsonResponse(ret)
#     return render(request, "login.html")

# 极验科技验证码视图
def login(request):
    if request.method == "POST":
        # print(request.POST)
        # 初始化ret字典
        ret = {"status": 0, "msg": ""}

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        username = request.POST.get("username")
        password = request.POST.get("password")
        vaild_code = request.POST.get("vaild_code")

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                ret["msg"] = "/index/"
                logger.info("用户 {} 登录成功".format(username))
            else:
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login2.html")

from cms import settings
import os
import requests
@login_required
def index(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        file_obj = request.FILES.get("package")
        filename = file_obj.name

        # 判断用户上传的文件名是否合法
        if filename.split(".")[-1] not in ["apk", "ipa"]:
            ret["status"] = 1
            ret["msg"] = "非法的文件名"
        else:
            path = os.path.join("/mnt/wwwroot/apk/", filename)
            with open(path, "wb") as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            # ret["msg"] = "上传成功"
            # ret["url"] = "http://cdn.pursedada.com/" + filename
            try:
                # 调用阿里云接口刷新CDN
                user_params = {
                    "Action": "RefreshObjectCaches",
                    "ObjectPath": "cdn.pursedada.com/"+filename,
                    "ObjectType": "File",
                }
                # print(user_params["ObjectPath"])
                cdn_server_address = "https://cdn.aliyuncs.com"

                params = aliyun.compose_url(user_params)
                res = requests.get(cdn_server_address, params=params)
                if res.status_code == 200:
                    ret["msg"] = "上传成功"
                    ret["url"] = "http://cdn.pursedada.com/"+filename
                    logger.info("用户 {} 上传了文件{}".format(request.user.username, filename))
                    logger.info("CDN刷新成功, {}".format(res.text))
                else:
                    ret["status"] = 1
                    ret["msg"] = "cdn刷新失败"
                    logger.info("CDN刷新失败, {}".format(json.loads(res.text)["Message"]))
            except Exception as e:
                ret["status"] = 1
                ret["msg"] = e
        return JsonResponse(ret)
    return render(request, "index.html")
    # return render(request, "test.html")


def logout(request):
    logger.info("用户 {} 登出!".format(request.user.username))
    auth.logout(request)
    return redirect("/index/")


# 生成验证码视图
def get_valid_img(request):
    # 定义随机获取颜色的函数
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    height = 180
    width = 35

    # 生成image对象
    img_obj = Image.new(
        'RGB',
        (height, width),
        get_random_color()
    )

    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件， 得到一个字体对象
    font_obj = ImageFont.truetype("static/font/kumo.ttf", 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(4):
        u = chr(random.randint(65, 90))  # 大写字母
        l = chr(random.randint(97, 122))  # 小写字母
        n = str(random.randint(0, 9))  # 数字

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20 + 40 * i, 0), tmp, fill=get_random_color(), font=font_obj)

    print("".join(tmp_list))
    print("生成的验证码".center(120, "="))

    # 将生成的验证码保存在session中
    request.session["vaild_code"] = "".join(tmp_list)

    # 将图片保存至内存中
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')

    data = io_obj.getvalue()
    return HttpResponse(data)

    # 请在官网申请ID使用，示例ID不可使用


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 注册视图函数(form表单提交)
# def register(request):
#     if request.method == "POST":
#         form_obj = forms.RegForm(request.POST)
#         if form_obj.is_valid():
#             form_obj.cleaned_data.pop("re_password")
#             models.UserInfo.objects.create_user(**form_obj.cleaned_data)
#             # return HttpResponse("注册成功")
#             return redirect("/login/")
#         else:
#             print(form_obj.errors)
#             return render(request, "register.html", {"form_obj": form_obj})
#     form_obj = forms.RegForm()
#     return render(request, "register.html", {"form_obj": form_obj})

# 注册视图(ajax提交)
def register(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        if form_obj.is_valid():
            # 获取用户上传的头像
            avatar_obj = request.FILES.get("avatar")
            print(avatar_obj)
            form_obj.cleaned_data.pop("re_password")
            if avatar_obj:
                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_obj)
            else:
                models.UserInfo.objects.create_user(**form_obj.cleaned_data)
            # return HttpResponse("注册成功")
            ret["msg"] = "/index/"
            logger.info("用户 {} 注册成功!".format(form_obj.cleaned_data["username"]))
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    form_obj = forms.RegForm()
    return render(request, "register.html", {"form_obj": form_obj})


# 专门用来检测用户名是否已注册的视图函数
def check_username_exist(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        username = request.POST.get("username")
        user = models.UserInfo.objects.filter(username=username)
        if user:
            ret["status"] = 1
            ret["msg"] = "用户名已被注册"
            return JsonResponse(ret)
        else:
            return JsonResponse(ret)


