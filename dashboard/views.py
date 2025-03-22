from django.shortcuts import render


def home_view(request):
    return render(request, 'dashboard/home.html')


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

