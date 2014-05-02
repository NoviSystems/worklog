from django.forms.forms import BoundField
from django.core.exceptions import ObjectDoesNotExist
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from forms import WorkItemForm
from models import Repo, Issue

@dajaxice_register
def update_repo_issues(request, repo_id, formid):
    dajax = Dajax()
    
    repo = Repo.objects.get(github_id=repo_id)
    issues = Issue.objects.filter(repo=repo).order_by('number')

    form = WorkItemForm(reminder=None, user=request.user)
    field = form.fields['issue']
    field.queryset = issues

    dajax.assign('#id_form-' + str(formid) + '-issue', 'outerHTML', str(BoundField(form, field,'form-' + str(formid) + '-issue')))
    
    return dajax.json()

@dajaxice_register
def initialize_issues(request, formid):
    dajax = Dajax()
    qs = Issue.objects.none()

    form = WorkItemForm(reminder=None, user=request.user)
    field = form.fields['issue']
    field.queryset = qs

    dajax.assign('#id_form-'+ str(formid) + '-issue', 'outerHTML', str(BoundField(form, field, 'form-' + str(formid) + '-issue')))
    return dajax.json()
