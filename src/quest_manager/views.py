from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.template import RequestContext, loader
from django.views.generic.edit import CreateView, DeleteView

from comments.models import Comment
from comments.forms import CommentForm

from .forms import QuestForm
from .models import Quest, QuestSubmission, TaggedItem

@login_required
def quest_list(request):
    # quest_list = Quest.objects.order_by('name')

    quest_list = Quest.objects.get_available(request.user)
    in_progress_submissions = QuestSubmission.objects.all_not_completed(request.user)
    completed_submissions = QuestSubmission.objects.all_completed(request.user)
    # output = ', '.join([p.name for p in quest_list])
    context = {
        "title": "Quests",
        "heading": "Quests",
        "quest_list": quest_list,
        "in_progress_submissions": in_progress_submissions,
        "completed_submissions": completed_submissions,
    }
    return render(request, "quest_manager/quests.html" , context)

@staff_member_required
def quest_create(request):
    form =  QuestForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('quests:quests')
    context = {
        "title": "Quests",
        "heading": "Create New Quest",
        "form": form,
        "submit_btn_value": "Create",
    }
    return render(request, "quest_manager/quest_form.html", context)

@staff_member_required
def quest_update(request, quest_id):
    quest_to_update = get_object_or_404(Quest, pk=quest_id)
    form = QuestForm(request.POST or None, instance = quest_to_update)
    if form.is_valid():
        form.save()
        return redirect('quests:quests')
    context = {
        "title": "Quests",
        "heading": "Update Quest",
        "form": form,
        "submit_btn_value": "Update",
    }
    return render(request, "quest_manager/quest_form.html", context)

@staff_member_required
def quest_copy(request, quest_id):
    new_quest = get_object_or_404(Quest, pk=quest_id)
    new_quest.pk = None # autogen a new primary key (quest_id by default)
    new_quest.name = "Copy of " + new_quest.name
    # print(quest_to_copy)
    # print(new_quest)
    # new_quest.save()

    form =  QuestForm(request.POST or None, instance = new_quest)
    if form.is_valid():
        form.save()
        return redirect('quests:quests')
    context = {
        "title": "Quests",
        "heading": "Copy a Quest",
        "form": form,
        "submit_btn_value": "Create",
    }
    return render(request, "quest_manager/quest_form.html", context)

@login_required
def start(request, quest_id):

    quest = get_object_or_404(Quest, pk=quest_id)
    new_sub = QuestSubmission.objects.create_submission(request.user, quest)
    if new_sub is None:
        raise Http404 #shouldn't get here
    return redirect('quests:submission', submission_id = new_sub.id)

@login_required
def complete(request, submission_id):
    sub = get_object_or_404(QuestSubmission, pk=submission_id)
    template_name = "quest_manager/questsubmission_confirm_delete.html"
    if sub.user != request.user:
        return redirect('quests:quests')
    sub.mark_completed()
    # return render(request, template_name, {'submission':sub})
    return redirect('quests:quests')

@login_required
def drop(request, submission_id):
    sub = get_object_or_404(QuestSubmission, pk=submission_id)
    template_name = "quest_manager/questsubmission_confirm_delete.html"
    if sub.user != request.user:
        return redirect('quests:quests')
    if request.method=='POST':
        sub.delete()
        return redirect('quests:quests')
    return render(request, template_name, {'submission':sub})

@login_required
def submission(request, submission_id):
    sub = QuestSubmission.objects.get(id = submission_id)
    if sub.user != request.user:
        return redirect('quests:quests')

    context = {
        "heading": sub.quest.name,
        "submission": sub,
        # "comments": comments,
        # "comment_form": comment_form
    }
    return render(request, 'quest_manager/submission.html', context)


@login_required
def detail(request, quest_id):
    #if there is an active submission, get it and display accordingly

    q = get_object_or_404(Quest, pk=quest_id)
    active_submission = QuestSubmission.objects.quest_is_available(request.user, q)
    #comments = Comment.objects.filter(quest=q)
    comments = q.comment_set.all() # can get comments from quest due to the one-to-one relationship
    # content_type = ContentType.objects.get_for_model(q)
    # tags = TaggedItem.objects.filter(content_type=content_type, object_id = q.id)
    comment_form = CommentForm(request.POST or None)

    context = {
        "heading": q.name,
        "q": q,
        "comments": comments,
        "comment_form": comment_form
    }
    return render(request, 'quest_manager/detail.html', context)

## Demo of sending email
# @login_required
# def email_demo(request):
#     subject = "Test email from Hackerspace Online"
#     from_email = ("Timberline's Digital Hackerspace <" +
#         settings.EMAIL_HOST_USER +
#         ">")
#     to_emails = [from_email]
#     email_message = "from %s: %s via %s" %(
#         "Dear Bloggins", "sup", from_email)
#
#     html_email_message = "<h1> if this is showing you received an HTML messaage</h1>"
#
#     send_mail(subject,
#         email_message,
#         from_email,
#         to_emails,
#         html_message = html_email_message,
#         fail_silently=False)
#
#     context = {
#         "email_to" : to_emails,
#         "email_from": from_email,
#         "email_message":email_message,
#         "html_email_message": html_email_message
#
#     }
#
#     return render(request, "email_demo.html", context)


##
