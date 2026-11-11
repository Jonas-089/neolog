from django.shortcuts import render, redirect

# for flash request to give user feedback for input
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm
from definitionen.models import Definition
from users.models import User


def register(request):

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():

            # saves user
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f'Dein Account wurde erstellt! Du kannst dich jetzt anmelden.')
            return redirect("login")

    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', context={'form': form})

@login_required
def profile(request, user):

    user = User.objects.get(username=user)
    current_user = request.user

    context = {'definitions': Definition.objects.filter(author=user).order_by('-date_posted'),
               'user': user,
               'current_user': current_user
               }

    return render(request, template_name='users/profile.html', context=context)


@login_required
def edit_profile(request):

    # if POST request, pass data to form
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Deine Daten wurden aktualisiert.')
            return redirect("edit-profile")

    # if request is GET, just show form
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {'u_form': u_form}

    return render(request, 'users/edit_profile.html', context=context)
