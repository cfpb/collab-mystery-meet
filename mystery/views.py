from django.contrib.auth.decorators import login_required
from dynamicresponse.response import render_to_response, RequestContext
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse, NoReverseMatch
from core.models import OfficeLocation, OrgGroup, Person
from mystery.models import Interest
from mystery.forms import InterestForm
import datetime


def _create_params(req):
    p = {'is_mystery': True, }
    return p


@login_required
def index(request):
    active_interests = Interest.objects.filter(
        owner=request.user,
        is_active=True)
    if active_interests.count() > 0:
        return _get_results_page(request, active_interests.latest('created'))
    else:
        return _get_form_page(request)


def _get_form_page(request):
    if request.method == 'POST':
        form_interest = Interest(owner=request.user)
        form = InterestForm(request.POST, instance=form_interest)

        if form.is_valid():
            interest = form.save()
            return _get_results_page(request, interest)
    else:
        form = InterestForm()

    params = _create_params(request)
    params['form'] = form
    return render_to_response('mystery-meet/index.html',
                              params,
                              context_instance=RequestContext(request))


def _get_results_page(request, interest_obj):
    params = _create_params(request)

    # find your last entered interest
    params['interest_obj'] = interest_obj

    if interest_obj.match:
        match_person = Person.objects.get(user=interest_obj.match.owner)
        params['match_person'] = match_person
        params['match_locations'] = list(set(interest_obj.locations.all())
                                         .intersection(set(interest_obj.match.locations.all())))
    return render_to_response('mystery-meet/match_result.html',
                              params,
                              context_instance=RequestContext(request))


def _deactivate(user, interest_id, url=None, kwargs=None):
    default_redirect = reverse('mystery:mystery')
    interest_obj = Interest.objects.get(id=interest_id)
    if interest_obj.owner == user:
        interest_obj.set_inactive()
        if url is not None:
            if kwargs is not None:
                url = url + "?"
                for key in kwargs:
                    url += key + "=" + kwargs[key] + ";"
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(default_redirect)


@login_required
def close_cancel(request, interest_id):
    return _deactivate(request.user, interest_id)


@login_required
def close_complete(request, interest_id):
    try:
        redirect_link = reverse('form_builder:respond', args=('we-met-up',))
        interest_obj = get_object_or_404(Interest, id=interest_id)

        kwargs = {'Who did you meet?': interest_obj.match.owner.get_full_name(),
                  'Meet type': interest_obj.for_what()}
        if interest_obj.video_chat:
            kwargs['Location'] = "Other"
        if interest_obj.locations.count() == 1:
            kwargs['Location'] = interest_obj.locations.all()[0].name
        elif interest_obj.match.locations.count() == 1:
            kwargs['Location'] = interest_obj.match.locations.all()[0].name

        return _deactivate(
            request.user, interest_id, redirect_link, kwargs=kwargs)

    except NoReverseMatch:
        return _deactivate(request.user, interest_id)


@login_required
def close_incomplete(request, interest_id):
    try:
        redirect_link = reverse(
            'form_builder:respond',
            args=(
                'it-didnt-work-out',
            ))
        interest_obj = get_object_or_404(Interest, id=interest_id)
        kwargs = {
            'Who was your match?': interest_obj.match.owner.get_full_name()}
        return _deactivate(
            request.user, interest_id, redirect_link, kwargs=kwargs)
    except NoReverseMatch:
        return _deactivate(request.user, interest_id)
