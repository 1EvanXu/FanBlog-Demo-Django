from django.http import HttpResponse
from django.shortcuts import render, redirect
from backstage.models import Manager
from backstage.forms import ManagerLoginForm


# Create your views here.


def login(request):
    return render(request, "backstage/login.html", {'manager_login_form': ManagerLoginForm()})


def login_validate(request):
    content = {
        "manager_login_form": ManagerLoginForm(),
        "message": "",
    }

    if request.method == 'POST':

        login_form = ManagerLoginForm(request.POST)
        content['manager_login_form'] = login_form

        if login_form.is_valid():
            login_email = login_form.cleaned_data['email']
            login_password = login_form.cleaned_data['password']
            is_remember = request.POST.get('remember')

            try:
                manager = Manager.objects.get(email=login_email)

                if login_password == manager.password:
                    request.session['admin'] = {'name': manager.name, 'level': manager.level}

                    # 如果登录时勾选了记住账户，则设置session存活时间为５天，　否则默认为6个小时
                    if is_remember == 'on':
                        request.session.set_expiry(432000)
                    else:
                        request.session.set_expiry(21600)

                    return redirect('backstage:index')
                else:
                    content['message'] = "密码错误"
                    return render(request, "backstage/login.html", content)
            except Manager.DoesNotExist:
                content['message'] = "用户不存在"
                return render(request, "backstage/login.html", content)
    return render(request, "backstage/login.html", content)


def logout(request):
    request.session.flush()
    return redirect('backstage:login')
