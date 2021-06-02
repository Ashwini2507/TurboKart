from django.shortcuts import render

# Create your views here.
def about(request):
#       return HttpResponse('<h1>About</h1>')
        return render(request, 'website/about.html',{'title':'About'})

def home(request):
#       return HttpResponse('<h1>About</h1>')
        return render(request, 'website/home.html',{'title':'Home'})

