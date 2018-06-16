from django.shortcuts import render

# def ETL():



# Create your views here.
def index(request):
    if request.method == "POST":


    return render(request, 'ETL.html')