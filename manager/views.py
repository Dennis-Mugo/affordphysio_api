from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.

@api_view(["get"])
def hello(request):
    return Response({"message": "hello world"})
