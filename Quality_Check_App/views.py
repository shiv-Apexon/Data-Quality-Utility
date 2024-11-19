from django.shortcuts import render

def index(request):
    if request.method == 'POST':
        pass
    return render(request, 'QCA/index.html')
