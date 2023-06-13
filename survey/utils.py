import logging
import random
import secrets
from asyncio.log import logger
from datetime import datetime, timedelta

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import F

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from survey.models import Participant

from .decorators import *
from .models import *

participantStatusDict = {
    "startSurvey": "",
    "democraticOpinion1": "awaitingDemocraticOpinion",
    "democraticOpinion2": "awaitingSecondDemocraticOpinion",
    "newsAccuracyTask": "awaitingNewsAccuracyTask",
    "waitingRoomNew": "awaitingToBecomeANode",
    "newsResponseInfo": [
        "isANode",
        "onNewsInfo",
    ],  # this view should have both permissions
    "newsResponse": ["isANode", "onNewsResponse"],
    "quizTask": "awaitingQuizTask",
    "earnings": "awaitingEarnings",
    "endOfSurvey": "",
    "noSpotsAvailable": "earlyGoodbye",
    # Added by Ranjeet
    "finish": "surveyCompleted"
}
User = get_user_model()


def create_new_user(request):
    try:
        username = secrets.token_hex(16)
        password = secrets.token_hex(16)
        user = User.objects.create_user(username, "myemail@crazymail.com", password)
        user.save()

        # get the user
        user = authenticate(username=username, password=password)

    except Exception as e:
        logging.exception(e)
        raise logging.exception("could not create a new user")
    else:
        return user


def get_current_participant(request):
    try:
        participant = Participant.objects.get(user=request.user)
    except Exception as e:
        logger.error(f"could not get current participant {e}")
        raise Exception(f"could not get current participant {e}")
    else:
        return participant


def get_participantViewLog(participant_id):
    participantViewLog = ParticipantViewLogs.objects.get(participant=participant_id)
    return participantViewLog


def create_new_participant(request, form, user):

    try:
        participant = Participant.objects.create(
            user=user,
            session=request.session.session_key,
            upiID=form.cleaned_data["upi_ID"]
            + "@"
            + form.cleaned_data["upi_ID_domain"],
            participantStatus="awaitingDemocraticOpinion",
        )
    except IntegrityError as e:
        raise e
    else:
        return participant


def process_democratic_opinion(request, form):
    """
    Get participant object, add democraticOpinion, add timestamp(update: not adding timestamp here, but adding it later before sending to waiting room),
    change status to:earlyKickoutBecauseNeutral or demorcaticOpinionForm2 and redirect
    """

    participant = get_current_participant(request)
    ### process democratic opinion form 1 here:
    # 1. make model fields, run migrations, put the form.cleaned data in those fields
    ####

    opinion = form.cleaned_data["democratic_Opinion"]
    participant.democaticOpinions = opinion
    if opinion == 0:
        opinion = "Strongly Disapprove"
    elif opinion == 25:
        opinion = "Disapprove"
    elif opinion == 50:
        opinion = "Neutral"
    elif opinion == 75:
        opinion = "Approve"
    elif opinion == 100:
        opinion = "Strongly Approve"

    democratic_form, created = DemocraticOpinion1.objects.get_or_create(
        participant=participant,
        news_source=form.cleaned_data["news_source"],
        affiliation=form.cleaned_data["affiliation"],
        democratic_Opinion=opinion,
    )
    try:
        democratic_form.save()
        participant.save()
    except Exception as e:
        logger.error(e)
        raise e
    else:
        return form.cleaned_data["democratic_Opinion"]


def process_democratic_opinion2(request, form):
    """
    Get participant object, add democraticOpinion, add timestamp,

    """
    try:
        participant = get_current_participant(request)
    except Exception as e:
        print(e)
    else:
        try:
            ### process democratic opinion form 3 here:
            ####
            democratic_form, created = DemocraticOpinion2.objects.get_or_create(
                participant=participant,
                age=form.cleaned_data["age"],
                gender=form.cleaned_data["gender"],
                religion=form.cleaned_data["religion"],
                state=form.cleaned_data["state"],
                district=form.cleaned_data["district"],
                highschool=form.cleaned_data["highschool"],
                edu_level=form.cleaned_data["edu_level"],
                course=form.cleaned_data["course"],
                checker=form.cleaned_data["checker"],
                voted=form.cleaned_data["voted"],
                social_media_apps=form.cleaned_data["social_media_apps"],
                time_spent=form.cleaned_data["time_spent"],
                sources=form.cleaned_data["sources"],
                sm_other=form.cleaned_data["sm_other"],
                tv_other=form.cleaned_data["tv_other"],
                onp_other=form.cleaned_data["onp_other"],
                np_other=form.cleaned_data["np_other"],
            )
            democratic_form.save()

            # participant.participantStatus = "awaitingSecondDemocraticOpinion"

            participant.save()
            print(participant.participantStatus)
        except Exception as e:
            logging.exception(f"could not save {participant.id}'s democratic opinion2")
            raise Exception(f"could not save {participant.id} democratic opinion2")


def sendToWatingRoom(request):
    currParticipant = get_current_participant(request)
    currParticipant.participantStatus = participantStatusDict["waitingRoomNew"]
    currParticipant.democaticOpinionResponseTime = (
        timezone.now()
    )  # now:entered the que at time
    currParticipant.save()
    participantViewLog = get_participantViewLog(currParticipant)
    participantViewLog.waitingRoomNewTS = datetime.now()
    participantViewLog.save()
    return currParticipant


def kickout1(request):

    try:
        participant = get_current_participant(request)
    except Exception as e:
        print(e)
    else:
        _treatement = participant.treatement
        Treatement = apps.get_model("survey", _treatement)
        if timezone.now() > participant.newsResponseInfoTimeLimit:
            participant.participantStatus = "timedOut"
            node = Treatement.objects.get(participant=participant.id)
            node.status = "awaitingParticipant"
            participant.save()
            node.save()

            print(f"{participant}timedout")
            return True


def kickout2(request):

    try:
        participant = get_current_participant(request)
    except Exception as e:
        print(e)
    else:
        _treatement = participant.treatement
        Treatement = apps.get_model("survey", _treatement)
        if timezone.now() > participant.newsResponseTimeLimit:
            participant.participantStatus = "timedOut"
            node = Treatement.objects.get(participant=participant.id)
            node.status = "awaitingParticipant"
            participant.save()
            node.save()

            print(f"{participant}timedout")
            return True


def get_newsResponseAllowedTime(participantObject):
    currentParticipant = participantObject
    _treatement = currentParticipant.treatement
    Treatement = apps.get_model("survey", _treatement)

    node = Treatement.objects.get(participant=currentParticipant.id)

    if _treatement == "AdHocNodes":
        tableLoadingTime = 1
    else:
        print(len(node.nodeID) * 1)
        tableLoadingTime = len(node.nodeID) * 1
        print(timedelta(seconds=tableLoadingTime))

    totalTime = (
        timedelta(seconds=25)  # instructions
        + timedelta(seconds=7)  # for news item
        + timedelta(seconds=tableLoadingTime)
        + timedelta(seconds=2)  # for banner "you got these many seconds)"
        + timedelta(seconds=120)  #
        + timedelta(seconds=2)  # just incase to sync up
    )
    print(f" tableLoadingTime is : {tableLoadingTime}, totalTime is {totalTime}")
    return totalTime
