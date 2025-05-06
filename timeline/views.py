from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import TimelinePost, Comment
from django.contrib import messages

class PostListView(LoginRequiredMixin, ListView):
    model = TimelinePost
    template_name = 'timeline/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

class PostDetailView(LoginRequiredMixin, DetailView):
    model = TimelinePost
    template_name = 'timeline/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = TimelinePost
    template_name = 'timeline/post_form.html'
    fields = ['content', 'image']
    success_url = reverse_lazy('timeline:timeline-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TimelinePost
    template_name = 'timeline/post_form.html'
    fields = ['content', 'image']
    success_url = reverse_lazy('timeline:timeline-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TimelinePost
    template_name = 'timeline/post_confirm_delete.html'
    success_url = reverse_lazy('timeline:timeline-home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user

@login_required
def like_post(request, pk):
    post = get_object_or_404(TimelinePost, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.get_like_count()})

@login_required
def share_post(request, pk):
    post = get_object_or_404(TimelinePost, pk=pk)
    if request.user in post.shares.all():
        post.shares.remove(request.user)
        shared = False
    else:
        post.shares.add(request.user)
        shared = True
    return JsonResponse({'shared': shared, 'count': post.get_share_count()})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(TimelinePost, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty!')
    return redirect('timeline:post-detail', pk=pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.user:
        post_pk = comment.post.pk
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('timeline:post-detail', pk=post_pk)
    messages.error(request, 'You can only delete your own comments!')
    return redirect('timeline:post-detail', pk=comment.post.pk)
