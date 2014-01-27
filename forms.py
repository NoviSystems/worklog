from django.forms import ModelForm, Select, Form, HiddenInput, Textarea, CharField
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from models import WorkItem, Job, Repo, Issue 
from django.db.models import Q
from django.forms import models

import datetime
import math
import random

class BadWorkItemForm(Exception):
    pass

class WorkItemForm(ModelForm):

    job = forms.ModelChoiceField(queryset=Job.objects.none(), empty_label="None") # empty queryset, overridden in ctor   
    repo = forms.ModelChoiceField(queryset=Repo.objects.all(), empty_label="None", required=False)
    issue = forms.ModelChoiceField(queryset=Issue.objects.none(), empty_label="None", required=False)

    job.widget.attrs['class'] = 'form-control'
    repo.widget.attrs['class'] = 'form-control'
    issue.widget.attrs['class'] = 'form-control'

    class Meta:
        model = WorkItem
        fields = ('hours','text','job','repo','issue')

    def __init__(self, *args, **kwargs):
        reminder = kwargs.pop("reminder")
        user = kwargs.pop("logged_in_user");
        super(WorkItemForm,self).__init__(*args,**kwargs)
        
        if reminder:
            queryset = reminder.get_available_jobs()
        else:
            queryset = Job.get_jobs_open_on(datetime.date.today())
        
        queryset = queryset.filter(Q(available_all_users=True)|Q(users__id=user.id)).distinct()
        queryset = queryset.order_by('name')
        self.fields["job"].queryset = queryset


        self.fields["hours"].widget.attrs['class'] = 'form-control'
        self.fields["text"].widget.attrs['class'] = 'form-control'

        self.fields["hours"].widget.attrs['placeholder'] = 'Hours Worked'
        self.fields["text"].widget.attrs['placeholder'] = 'Work Description'

        self.fields["hours"].widget.attrs['style'] = 'width: 200px;'
        self.fields["text"].widget.attrs['style'] = 'width: 300px;'

        if args: 
            data = args[0]
        else:
            data = kwargs.get('data')

        if data:
            repo_id = data.get('repo')
            if repo_id:
                repo = Repo.objects.get(github_id=repo_id)
                self.fields["issue"].queryset = Issue.objects.filter(repo=repo)


    def clean(self):
        cleaned_data = super(WorkItemForm, self).clean()
        try:
            hours = cleaned_data["hours"]
        except KeyError:
            hours = 0
        try:
            text = cleaned_data["text"]
        except KeyError:
            text = None
        try:
            job = cleaned_data["job"]
        except KeyError:
            job = None

        # Only allows non-zero, non-negative hours to be entered in half hour increments.
        if (hours % 1 != 0.5) and (hours % 1 != 0):
            message_list = ["Please, Hammer, don't hurt 'em! Use half-hour increments.", 
                            "All your mantissa are belong to us. Half hour increments only. Please.", 
                            "You thought we wouldn't notice that you didn't use half hour increments. You were wrong. Try again, jerk.", 
                            "Ceterum censeo numerum esse tibi delendum! Dimidiae incrementuli horae uti, amabo.",
                            "Hey buddy. How's it going? Listen, not a huge deal, but we've got this thing where we use half hour increments.",
                            "If you could go ahead and use half hour increments, that would be grrrreeaat.",
                            "Your input rapes teenagers in Indochina. Half hour increments don't."]
            error_message = message_list[random.randint(0, len(message_list) - 1)]
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]
        elif hours < 0:
            error_message = "We here at <Insert Company Name here>  would like you to have a non-negative work experience. Please enter a non-negative number of hours."
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]
        elif not hours:
            error_message = "If you work at <Insert Company Name here>, you're more hero than zero. Enter an hero number of hours."
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]
        
        # Custom error messages for empty fields
        if text == None:
            error_message = "This is where you describe the work you did when you weren't on r/banana, you pickle-hating scum."
            self._errors["text"] = self.error_class([error_message])
            if text:
                del cleaned_data["text"]
        
        if job == None:
            error_message = "i.e., the thing you're supposed to wear pants for, but you probably don't, since you're a programmer."
            self._errors["job"] = self.error_class([error_message])
            if text:
                del cleaned_data["job"]
        
        return cleaned_data
