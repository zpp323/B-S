from django.shortcuts import render, redirect


# Create your views here.
from register import models


def loginredirection(req):
    return redirect('log/')

def log(req):
    if req.method == 'GET':
        return render(req, 'loginpage.html', {
            'web_title':'login',
            'register_success':'',
            'login_fail':'n'
        })
    else:
        username = req.POST.get('name')
        password = req.POST.get('password')
        result = models.User.objects.filter(username=username,password=password)
        print(result)
        if len(result)==1:
            session = req.session
            session['user'] = {'user':result.first().id}
            return redirect('../../workspace/')
        else:
            return render(req, 'loginpage.html', {
                'web_title': 'login',
                'register_success': '',
                'login_fail':'y'
            })

def reg(req):
    if req.method == "GET":
        return render(req, 'registerpage.html', {
            'web_title':'register',
            'retext': ''
        })
    else:
        username = req.POST.get("name")
        password = req.POST.get("password")
        password1 = req.POST.get("password1")
        print(username,password,password1)
        retext = ''
        userr = 0
        for i in range(len(username)):
            if (ord(username[i])<48 or ord(username[i])>57) and (ord(username[i])<97 or ord(username[i])>122):
                userr = 1
                break
        #name
        if len(username)<6 or len(username)>20:
            retext = "☞用户名请输入6-20个字符"
        elif ord(username[0])>=48 and ord(username[0])<=57:
            retext = "✘用户名首字母不能为数字"
        elif userr == 1:
            retext = "✘用户名只能是小写字母与数字"
        #password
        elif len(password)<6 or len(password)>20:
            retext = "☛密码请输入6-20个字符内"
        elif password!=password1:
            retext = "✘两次密码不一致"
        if retext!='':
            return render(req, 'registerpage.html', {
                'web_title': 'login',
                'retext': retext
            })
        else:
            models.User.objects.create(username=username, password=password)
            return render(req, 'loginpage.html', {
                'web_title': 'login',
                'register_success':'ok',
                'login_fail':'n'
            })



