from django.shortcuts import render

# def ETL():



# Create your views here.
def index(request):
    return render(request, 'ETL.html')


def searchbyentity(request):
    return render(request, 'searchbyactor.html')