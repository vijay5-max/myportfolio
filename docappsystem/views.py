from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

from dasapp.EmailBackEnd import EmailBackEnd
from dasapp.models import CustomUser, Appointment

User = get_user_model()


# ==========================
# BASE & AUTH VIEWS
# ==========================
def BASE(request):
    return render(request, 'base.html')


def LOGIN(request):
    return render(request, 'login.html')


def doLogin(request):
    if request.method == 'POST':
        user = EmailBackEnd.authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)

            if user.user_type == '1':
                return redirect('admin_home')
            elif user.user_type == '2':
                return redirect('doctor_home')
            elif user.user_type == '3':
                return redirect('user_home')

        messages.error(request, 'Email or Password is not valid')
        return redirect('login')

    return redirect('login')


def doLogout(request):
    logout(request)
    return redirect('login')


# ==========================
# PROFILE
# ==========================
@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, 'profile.html', {'user': user})


@login_required(login_url='/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        try:
            user = CustomUser.objects.get(id=request.user.id)

            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')

            if request.FILES.get('profile_pic'):
                user.profile_pic = request.FILES.get('profile_pic')

            user.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')

        except Exception:
            messages.error(request, "Profile update failed")

    return render(request, 'profile.html')


# ==========================
# CHANGE PASSWORD
# ==========================
@login_required(login_url='/')
def CHANGE_PASSWORD(request):
    if request.method == "POST":
        current = request.POST.get("cpwd")
        new_pass = request.POST.get("npwd")

        user = User.objects.get(id=request.user.id)

        if user.check_password(current):
            user.set_password(new_pass)
            user.save()
            login(request, user)
            messages.success(request, "Password changed successfully")
        else:
            messages.error(request, "Current password is incorrect")

        return redirect("change_password")

    return render(request, 'change-password.html')


# ==========================
# APPOINTMENT BOOKING (NO tzinfo ERROR)
# ==========================
@login_required(login_url='/')
def BOOK_APPOINTMENT(request):
    if request.method == "POST":
        try:
            doctor_id = request.POST.get('doctor')
            date_str = request.POST.get('appointment_date')  # yyyy-mm-dd
            time_str = request.POST.get('appointment_time')  # hh:mm

            # ✅ Convert STRING → DATETIME
            dt = datetime.strptime(
                f"{date_str} {time_str}",
                "%Y-%m-%d %H:%M"
            )

            # ✅ Make timezone-aware
            appointment_datetime = timezone.make_aware(dt)

            Appointment.objects.create(
                user=request.user,
                doctor_id=doctor_id,
                appointment_date=appointment_datetime,
                status="Pending"
            )

            messages.success(request, "Appointment booked successfully")
            return redirect('user_home')

        except Exception as e:
            messages.error(request, f"Error booking appointment: {e}")
            return redirect('appointment')

    return render(request, 'appointment.html')
