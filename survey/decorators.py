from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.base import ObjectDoesNotExist
from .models import Participant

participantStatus = [
    "awaitingDemocraticOpinion",
    "awaitingToBecomeANode",
    "isANode",
    "timedOut",
    "earlyGoodbye",
    "surveyCompleted",
]


def permission_isAnonUser(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            participant = Participant.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/surveyRouter/")

    return wrap


def permission_awaitingDemocraticOpinion(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            participant = Participant.objects.get(user=request.user)
        except TypeError:
            return HttpResponseRedirect("/startSurvey/")
        else:
            if participant.participantStatus == "awaitingDemocraticOpinion":
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect("/surveyRouter/")

    return wrap

def permission_awaitingSecondDemocraticOpinion(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            participant = Participant.objects.get(user=request.user)
        except TypeError:
            return HttpResponseRedirect("/startSurvey/")
        else:
            if participant.participantStatus == "awaitingSecondDemocraticOpinion":
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect("/surveyRouter/")

    return wrap


def permission_awaitingToBecomeANode(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            participant = Participant.objects.get(user=request.user)
        except TypeError:
            return HttpResponseRedirect("/startSurvey/")
        else:
            if participant.participantStatus == "awaitingToBecomeANode":
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect("/surveyRouter/")

    return wrap


def permission_isANode(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            participant = Participant.objects.get(user=request.user)
        except TypeError:
            return HttpResponseRedirect("/startSurvey/")

        else:
            if participant.participantStatus == "isANode":
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect("/surveyRouter/")

    return wrap
