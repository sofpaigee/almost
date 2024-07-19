from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from blog.models import Resource
from users.forms import ResourceUpload, ResourceUpdateForm
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)

def home(request):
    context = {
        'resource': Resource.objects.all(),
    }
    return render(request, 'blog/home.html', context)

def resource_list(request):
    search_query = request.GET.get('q')
    if search_query:
        resources = Resource.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('-date_uploaded')  
    else:
        resources = Resource.objects.order_by('-date_uploaded')  

    return render(request, 'blog/resource_list.html', {'resources': resources})

@login_required

def upload_resource(request):
    if request.method == 'POST':
        form = ResourceUpload(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.author = request.user
            resource.subject = form.cleaned_data.get('subjects')
            resource.save()
            print("Resource uploaded:", resource)
            return redirect('resource_list')
    else:
        form = ResourceUpload()
    return render(request, 'blog/resource_upload.html', {'form': form})


class ResourceListView(ListView): 
    model = Resource
    template_name = 'blog/resource_list.html'
    context_object_name = 'resources'
    ordering = ['-date_uploaded']
    paginate_by = 1

class UserResourceListView(ListView):  
    model = Resource
    template_name = 'blog/user_resource_list.html'
    context_object_name = 'resources'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Resource.objects.filter(author=user).order_by('-date_uploaded')

class ResourceDetailView(DetailView):
    model = Resource

class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Resource
    form_class = ResourceUpdateForm
    template_name = 'blog/update_resource.html' 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial_file'] = self.object.file
        return kwargs

    def form_valid(self, form):
        if 'file' in self.request.FILES:
            form.instance.file = self.request.FILES['file']
        return super().form_valid(form)

    def test_func(self):
        resource = self.get_object()
        return self.request.user == resource.author

    def get_success_url(self):
        return reverse('resource-detail', kwargs={'pk': self.object.pk})

class ResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Resource
    template_name = 'blog/resource_confirm_delete.html'
    success_url = reverse_lazy('resource_list')

    def test_func(self):
        resource = self.get_object()
        return self.request.user == resource.author

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
 
