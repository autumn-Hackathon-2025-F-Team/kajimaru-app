from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

def welcome(request): return HttpResponse("welcome")
def join_verify(request): return redirect("profiles")
def signup(request): return HttpResponse("signup")
def profiles(request): return HttpResponse("profiles")
def profile_enter(request, pk: int): return redirect("dashboard")
def profile_exit(request): return redirect("profiles")
def dashboard(request): return HttpResponse("dashboard")
