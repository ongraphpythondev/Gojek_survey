import logging
import random
import secrets
from ast import Try
from asyncio.log import logger
from cgi import parse_multipart
from datetime import datetime, timedelta
from multiprocessing import context
from xmlrpc.client import DateTime

from click import ParamType
from django import views
from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import F

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from channels.db import database_sync_to_async
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.urls import reverse

import survey
from survey import urls
from survey.models import NewsResponse, Participant, Quiz, Treatment

from .decorators import *
from .forms import (
    DemocraticOpinionForm1,
    DemocraticOpinionForm2,
    NewsAccuracyTaskForm,
    NewsResponseForm,
    NewsResponseInfoForm,
    QuizForm,
    StartSurveyForm,
    UPIIDForm,
    EarningForm
)
from .models import (
    C0,
    T1_L,
    T1_R,
    T2,
    AdHocNodes,
    AllotmentLogs,
    DemocraticOpinion1,
    DemocraticOpinion2,
    Earnings,
    Everything,
    NewsResponse,
    Participant,
    ParticipantViewLogs,
    Quiz,
    Tracker2,
    User,
)
from .utils import (
    create_new_participant,
    create_new_user,
    get_current_participant,
    get_newsResponseAllowedTime,
    get_participantViewLog,
    kickout1,
    kickout2,
    participantStatusDict,
    process_democratic_opinion,
    process_democratic_opinion2,
    sendToWatingRoom,
)
from .utils_allotmentLogic import *

participantStatus = [
    "awaitingDemocraticOpinion",
    "awaitingToBecomeANode",
    "isANode",
    "timedOut",
    "earlyGoodbye",
    "earlyGoodbyeExceedsThreshold",
    "surveyCompleted",
]


ROUTING_PERMISSIONS = True
KICKOUT_TIMER = True
DEV_MODE = False  # dont use

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)


User = get_user_model()
# Create your views here.
from django.views.decorators.cache import never_cache


@never_cache
def startSurvey(request):
    if request.user.is_anonymous:
        print("is anon")

    print(f"startSurvey:{request.user}")
    """
    Creates a new user with a random 16 char hex encoded user name and password and authenticate them.
    create a new participant Object
    """
    # import pdb; pdb.set_trace()
    if request.method == "POST":

        # Added by Ranjeet
        countActive = Treatment.objects.filter(isActive=False).count()
        if countActive == 6:
            print("Waiting for the admin to start the session, please wait")
            return HttpResponseRedirect("/sessionNotAvailable/")
        
        form = StartSurveyForm(request.POST)
        if form.is_valid():
            if request.user.is_anonymous:
                try:
                    user = create_new_user(request)
                except Exception as e:
                    print(e)
                    logger.error(e)
                    return HttpResponse(
                        "something went wrong, please close the browser and try again"
                    )
                else:
                    try:
                        participant = create_new_participant(request, form, user)
                    except IntegrityError as e:
                        print(e)
                        logging.exception(e)
                        form = StartSurveyForm()

                        # in this case, pop up a message saying upi ID exists to the user
                        messages.warning(
                            request,
                            "this UPI ID has already been used. Please enter another",
                        )
                        return render(
                            request=request,
                            template_name="survey/startSurvey.html",
                            context={
                                "form": form,
                            },
                        )

                    else:
                        login(request, user)
                        participant.participantStatus == participantStatusDict[
                            "democraticOpinion1"
                        ]
                        participantViewLog = ParticipantViewLogs.objects.create(
                            participant=participant, democraticOpinion1TS=datetime.now()
                        )
                        participantViewLog.save()
                        participant.save()
                        return HttpResponseRedirect("/democraticOpinion/")

            # if the user is not anonynous and we have an authenticated user
            else:
                try:
                    get_current_participant(request)
                except Exception as e:
                    logger.error("ERror",e)
                    # handle is user is authenticated but not a participant yet.
                    # create a new p
                else:
                    response = HttpResponseRedirect("/democraticOpinion/")
                    return response

            # redirect to a new URL:

    else:
        form = StartSurveyForm()

    return render(
        request=request,
        template_name="survey/startSurvey.html",
        context={"form": form},
    )


def surveyRouter(request):
    if request.method == "GET":
        # import pdb; pdb.set_trace()

        try:
            participant = Participant.objects.get(user=request.user)
            participantStatus = participant.participantStatus
        except TypeError:
            return HttpResponseRedirect("/startSurvey/")
        else:
            if participantStatus == "awaitingDemocraticOpinion":
                return HttpResponseRedirect("/democraticOpinion1/")
            elif participantStatus == "awaitingSecondDemocraticOpinion":
                return HttpResponseRedirect("/democraticOpinion2/")
            elif participantStatus == participantStatusDict["newsAccuracyTask"]:
                return HttpResponseRedirect("/newsAccuracyTask/")
            elif participantStatus == participantStatusDict["waitingRoomNew"]:
                return HttpResponseRedirect("/waitingRoomNew/")
            elif (
                participantStatus == participantStatusDict["newsResponseInfo"][0]
                and participant.newsStatus
                == participantStatusDict["newsResponseInfo"][1]
            ):
                return HttpResponseRedirect("/newsResponseInfo")
            elif (
                participantStatus == participantStatusDict["newsResponse"][0]
                and participant.newsStatus == participantStatusDict["newsResponse"][1]
            ):
                return HttpResponseRedirect("/newsResponse")
            elif participantStatus == participantStatusDict["quizTask"]:
                return HttpResponseRedirect("/quizTask")
            elif participantStatus == participantStatusDict["earnings"]:
                return HttpResponseRedirect("/earnings/")
            # Added by Ranjeet
            elif participantStatus == participantStatusDict["finish"]:
                return HttpResponseRedirect("/finish")

            # early kickouts or timed out views---
            elif participantStatus == "earyKickoutBecauseNeutral":
                return HttpResponseRedirect("/noSpotsAvailable/")
            elif participantStatus == "timedOut":
                return HttpResponseRedirect("/endOfSurvey/")

            elif (
                participantStatus == "earlyGoodbye"
            ):  # too far up in the queue, or spots finished
                return HttpResponseRedirect("/noSpotsAvailable")

            elif participantStatus == "surveyCompleted":
                return HttpResponse("You have already completed the survey")

            else:
                logger.error(
                    f"Participant {participant.id}'s status is {participantStatus}"
                )

                return HttpResponse("something went wrong")
        # return HttpResponse("You do not have permissions to view this page")


@never_cache
@login_required
@transaction.atomic
def democraticOpinion1(request):

    """
    View to get democratic Opinion and then send to democraticOpinion2 or early exit for neutrals
    """

    if request.method == "POST":
        form = DemocraticOpinionForm1(request.POST)
        # check whether it's valid:
        if form.is_valid():
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["democraticOpinion1"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")
            # import pdb; pdb.set_trace()
            # process the data in form.cleaned_data as required
            try:
                democraticOpinion = process_democratic_opinion(request, form)
            except Exception as e:
                return HttpResponse("something went wrong")
                # response.set_cookie("ID", form.cleaned_data["upi_ID"])

            else:
                currParticipant = get_current_participant(request)
                if int(democraticOpinion) == 50:
                    currParticipant.participantStatus = "earyKickoutBecauseNeutral"
                    currParticipant.save()
                    participantViewLog = get_participantViewLog(currParticipant)
                    participantViewLog.noSpotsAvailableTS = datetime.now()
                    participantViewLog.save()
                    currParticipant.save()

                    return HttpResponseRedirect("/noSpotsAvailable/")

                else:
                    # ideal: disabled rn because seconddemocraticOpinionForm is not working
                    currParticipant.participantStatus = (
                        "awaitingSecondDemocraticOpinion"
                    )

                    participantViewLog = get_participantViewLog(currParticipant)
                    participantViewLog.democraticOpinion2TS = datetime.now()
                    participantViewLog.save()
                    currParticipant.save()
                    if DEV_MODE == True:
                        return HttpResponseRedirect("/newsAccuracyTask/")
                    return HttpResponseRedirect("/democraticOpinion2/")
                    # participant.participantStatus = participantStatusDict["newsAccuracyTask"]
                    # participant.save()
                    # return HttpResponseRedirect("/newsAccuracyTask/")

    # if a GET (or any other method) we'll create a blank form
    else:
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                print("STATUS",participant,participant.participantStatus)
                if (
                    participant.participantStatus
                    != participantStatusDict["democraticOpinion1"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")

        form = DemocraticOpinionForm1()

    return render(
        request=request,
        template_name="survey/democraticOpinion1.html",
        context={"form": form},
    )


# @permission_awaitingSecondDemocraticOpinion
@never_cache
@login_required
def democraticOpinion2(request):
    if request.method == "POST":
        form = DemocraticOpinionForm2(request.POST)
        # ideal folow:
        if form.is_valid():
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["democraticOpinion2"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")
            try:
                process_democratic_opinion2(request, form)
            except:
                return HttpResponse("something went wrong")
            else:
                participant = get_current_participant(request)
                participant.participantStatus = participantStatusDict[
                    "newsAccuracyTask"
                ]
                participant.totalEarnings = 50
                participant.save()
                participantViewLog = get_participantViewLog(participant)
                participantViewLog.newsAccuracyTaskTS = datetime.now()
                participantViewLog.save()

                return HttpResponseRedirect("/newsAccuracyTask/")

    else:
        try:
            participant = get_current_participant(request)
        except:
            print("exception happened")
        else:
            if (
                participant.participantStatus
                != participantStatusDict["democraticOpinion2"]
            ):
                return HttpResponseRedirect("/surveyRouter/")
        form = DemocraticOpinionForm2()

    return render(
        request=request,
        template_name="survey/democraticOpinion2.html",
        context={"form": form},
    )


@never_cache
@login_required
def newsAccuracyTask(request):

    if request.method == "POST":
        form = NewsAccuracyTaskForm(request.POST)
        if form.is_valid:
            if ROUTING_PERMISSIONS == True:
                try:
                    participant = get_current_participant(request)
                except:
                    print("exception happened")
                else:
                    if (
                        participant.participantStatus
                        != participantStatusDict["newsAccuracyTask"]
                    ):
                        return HttpResponseRedirect("/surveyRouter/")

            try:
                # put into que and change status
                participant = sendToWatingRoom(request)
            except:
                return HttpResponse("something went wrong")
            else:
                return HttpResponseRedirect("/waitingRoomNew/")

    else:
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["newsAccuracyTask"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")
        form = NewsAccuracyTaskForm()

    return render(
        request=request,
        template_name="survey/newsAccuracyTask.html",
        context={"form": form},
    )


# @permission_awaitingToBecomeANode
@never_cache
@login_required
def waitingRoomNew(request):

    if request.method == "GET":
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["waitingRoomNew"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")

        message = "please wait and do not refresh the page"

        return render(
            request=request,
            template_name="survey/waitingRoomNew.html",
            context={"message": message},
        )


@login_required
@never_cache
def allotmentLogic2(request):
    if request.method == "GET":
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["waitingRoomNew"]
                ):
                    return HttpResponseRedirect("/surveyRouter/")

        currentParticipant = Participant.objects.get(user=request.user)
        print(f"current participant status is: {currentParticipant.participantStatus}")
        print(f"tratement is: {currentParticipant.treatement}")
        Log, created = AllotmentLogs.objects.get_or_create(
            participant=currentParticipant
        )

        # logic begins here

        tracker = checkTrackerForTreatementAndSpots(currentParticipant)
        if not tracker:
            # redirect out, change participant status
            print(
                f"no treatemets available{tracker},{currentParticipant.upiID} has to be redirected out"
            )
            currentParticipant.participantStatus = "earlyGoodbye"
            currentParticipant.save()
            response = HttpResponse()
            response["HX-Redirect"] = "/noSpotsAvailable/"
            return response

        elif tracker:
            print(f"treatemets available are:{tracker}")

            firstParticipant = checkIfFirstParticipant(currentParticipant)
            # Added by Ranjeet
            # Added Node is active or Not
            activeNodes = Treatment.objects.filter(isActive=True).values_list("treatmentNodeName")
            activeNodes = [i[0] for i in activeNodes]
            tracker = [i for i in tracker[0] if i in activeNodes]
            print(f"treatemets available with active:{tracker}")
            if tracker:
                treatement = selectTreatement(tracker)
            else:
                response = HttpResponse()
                response["HX-Redirect"] = "/kickout/"
                return response
            
            print(f"ActiveNodes are:{activeNodes}")
            print(f"{currentParticipant.upiID}'s treatement is :{treatement}")

            

            if treatement in activeNodes:
                if not firstParticipant:
                    print(f"{currentParticipant.upiID} is not the first participant")
                    threshold = isUnderThreshold(tracker, currentParticipant)
                    if not threshold:
                        # change this to create a new node and collect response
                        # -----allot to an adhoc node-----
                        print("creating an adhoc node")
                        openNode = AdHocNodes.objects.create(
                            participant=currentParticipant,
                        )
                        actually_allot_node(
                            openNode, currentParticipant, treatement="AdHocNodes"
                        )
                        response = HttpResponse()
                        response["HX-Redirect"] = "/newsResponseInfo/"
                        return response
                        # ----------------------------------

                        # redirect and change participant status to early exit
                    elif threshold:
                        message = "please wait, do not refresh the page"
                        print("you are in the threshold limit, please wait")

                        # message = please wait and do not refresh
                elif firstParticipant:
                    print(f"{currentParticipant.upiID} is the first participant")
                    # treatement = selectTreatement(tracker)
                    print(f"{currentParticipant.upiID}'s treatement is :{treatement}")

                    if treatement in ("T2", "C0"):
                        politicalLeaning = (
                            "left" if currentParticipant.democaticOpinions < 50 else "right"
                        )
                        openNode = openNodesT2(treatement, politicalLeaning)

                    else:
                        openNode = openNodes(treatement)

                    if not openNode:
                        print(Log.triesCheckOpenNodes)
                        print(type(Log.triesCheckOpenNodes))
                        print(int(Log.triesCheckOpenNodes))
                        tries = Log.triesCheckOpenNodes
                        Log.triesCheckOpenNodes = F("triesCheckOpenNodes") + 1
                        Log.save()
                        Log.refresh_from_db()

                        print(f"no open nodes in {treatement}")
                        if Log.triesCheckOpenNodes > 15:
                            # -----allot to an adhoc node-----
                            print("creating an adhoc node")
                            openNode = AdHocNodes.objects.create(
                                participant=currentParticipant,
                            )
                            actually_allot_node(
                                openNode, currentParticipant, treatement="AdHocNodes"
                            )
                            response = HttpResponse()
                            response["HX-Redirect"] = "/newsResponseInfo/"
                            return response
                            #.   ----------------------------------

                        deadNodeAndParticipant = deadNodes(treatement)
                        if deadNodeAndParticipant:
                            resetDeadNodeAndParticipant(deadNodeAndParticipant)
                            print("deadnodes were present and reset")

                        else:
                            print("please wait and do not refresh the page")
                    
                    elif openNode:
                        print(f"open nodes are there available in {treatement}")
                        actually_allot_node(openNode, currentParticipant, treatement)
                        response = HttpResponse()
                        response["HX-Redirect"] = "/newsResponseInfo/"
                        return response
                    # redirect to news response

        return HttpResponse("new allotment logic")


import random

# added function for news response info
@never_cache
@login_required
def newsResponseInfo(request):

    currentParticipant = get_current_participant(request)
    currentParticipantTreatement = currentParticipant.treatement
    context = {"treatement": currentParticipantTreatement}

    if request.method == "POST":
        form = NewsResponseInfoForm(request.POST)
        if form.is_valid():

            if ROUTING_PERMISSIONS == True:
                try:
                    participant = get_current_participant(request)
                except:
                    print("exception happened")
                else:
                    if (
                        participant.participantStatus
                        != participantStatusDict["newsResponseInfo"][0]
                    ) and (
                        participant.newsStatus
                        != participantStatusDict["newsResponseInfo"][1]
                    ):
                        return HttpResponseRedirect("/surveyRouter/")

            try:
                currentParticipant = get_current_participant(request)
                currentParticipant.participantStatus = "isANode"
                currentParticipant.newsStatus = "onNewsResponse"
                currentParticipant.newsResponseTimeLimit = (
                    timezone.now() + get_newsResponseAllowedTime(currentParticipant)
                )
                print(
                    f"newsResponseTimeLimit is {currentParticipant.newsResponseTimeLimit}"
                )
                currentParticipant.save()
                participantViewLog = get_participantViewLog(currentParticipant)

                participantViewLog.newsResponseTS = datetime.now()
                participantViewLog.save()
            except Exception as e:
                print(e)
                logger.error(e)
                logger.error("something went wrong ")
                return HttpResponse("something went wrong ")
            else:
                return HttpResponseRedirect("/newsResponse/")

    else:
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["newsResponseInfo"][0]
                ) and (
                    currentParticipant.newsStatus
                    != participantStatusDict["newsResponseInfo"][1]
                ):
                    return HttpResponseRedirect("/surveyRouter/")

        currentParticipant = get_current_participant(request)
        currentParticipantTreatement = currentParticipant.treatement
        context = {"treatement": currentParticipantTreatement}
        form = NewsResponseInfoForm()

    return render(
        request=request,
        template_name="survey/newsResponseInfo.html",
        context={"form": form, "context": context},
    )


def timerNewsResponse(request):
    """
    View to kickout a participant from NewsResponse from the frontend side
    if they do not reply  withing the time-limit and redirect them to endOfSurvey
    Note: This view relies on polling the server every 15 seconds from the front end.
    So if the participant closes the window, or their laptop catches fire,
    they will not poll the server and hence will not get kicked out.
    They essentially become a "dead node".This view does not handle that,
    resetting of dead nodes and particpant is handled by the allotment logic.
    """
    if request.method == "GET":
        try:
            participant = get_current_participant(request)
        except Exception as e:
            print(e)
        else:
            # redirect if timelimit reached, change user status, reset Node
            if (
                participant.newsStatus == "onNewsInfo"
                and participant.newsResponseInfoTimeLimit
            ):
                if KICKOUT_TIMER and kickout1(participant):
                    response = HttpResponse()
                    response["HX-Redirect"] = "/endOfSurvey/"
                    return response
                else:
                    pass

            elif (
                participant.newsStatus == "onNewsResponse"
                and participant.newsResponseTimeLimit
            ):
                if KICKOUT_TIMER and kickout2(participant):
                    response = HttpResponse()
                    response["HX-Redirect"] = "/endOfSurvey/"
                    return response
                else:
                    pass

    return HttpResponse("keep going")


def testingRoom(request):
    if request.method == "GET":

        currentParticipant = get_current_participant(request)
        currentParticipant.newsResponseTimeLimit = (
            timezone.now() + get_newsResponseAllowedTime(currentParticipant)
        )
        print(f"newsResponseTimeLimit is {currentParticipant.newsResponseTimeLimit}")

        return HttpResponse("you are in testing room")


# @permission_isANode
@never_cache
@login_required
def newsResponse(request):

    _treatement = Participant.objects.get(user=request.user).treatement
    print(f"_treatemet: {_treatement}")
    Treatement = apps.get_model("survey", _treatement)
    print(f"Treatemet: {Treatement}")
    participant_id = Participant.objects.get(user=request.user).id
    node = Treatement.objects.get(participant=participant_id)
    # print(node)
    # if node.child1ID :
    #     print(f"YES CHILD EXIST and is {node.child1ID}")

    # if node.child2ID:
    #     print(f"YES CHILD EXIST and is {node.child2ID}")
    #     pass
    # ----debugging stuff above

    # if this is a POST request we need to process the form data
    if request.method == "POST":

        def reduceTracker(treatement):
            """
            Reduces the tracker.
            If C0:
                reduce noPreferenceSpots
            If T1_L:
                reduce left spots
            If T1_R:
                reduce right spots
            If T2:
                if participant.democaticOpinions<50:
                    reduce left spots  
                if participant.democaticOpinions>50:
                    reduce right spots
            If Adhoc:
                do nothing, just collect info
            Input:
            __string__(treatement name): treatement name ad defined in Tracker2 class
            """

            if treatement == "AdHocNodes":
                pass
            else:
                tracker = Tracker2.objects.get(treatementName=treatement)
                print(tracker)

                if treatement == "C0":
                    # Added by Ranjeet
                    print("reducing C0 tracker by 1")
                    tracker.noPreferenceSpots = F("noPreferenceSpots") - 1

                    # if currentParticipant.democaticOpinions < 50:
                    #     tracker.leftSpots = F("leftSpots") - 1
                    # elif currentParticipant.democaticOpinions > 50:
                    #     tracker.rightSpots = F("rightSpots") - 1
                elif treatement == "T1_L":
                    print("reducing T1_L tracker by 1")
                    tracker.leftSpots = F("leftSpots") - 1
                elif treatement == "T1_R":
                    print("reducing T1_R tracker by 1")
                    tracker.rightSpots = F("rightSpots") - 1
                elif treatement == "T2":
                    if currentParticipant.democaticOpinions < 50:
                        tracker.leftSpots = F("leftSpots") - 1
                    elif currentParticipant.democaticOpinions > 50:
                        tracker.rightSpots = F("rightSpots") - 1

                tracker.save()

        # create a form instance and populate it with data from the request:
        form = NewsResponseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            if ROUTING_PERMISSIONS == True:
                try:
                    participant = get_current_participant(request)
                except:
                    print("exception happened")
                else:
                    if (
                        participant.participantStatus
                        != participantStatusDict["newsResponse"][0]
                    ) and (
                        participant.newsStatus
                        != participantStatusDict["newsResponse"][1]
                    ):
                        return HttpResponseRedirect("/surveyRouter/")

            # get the node based on participant id
            participant_id = Participant.objects.get(user=request.user).id
            node = Treatement.objects.get(participant=participant_id)
            print("FORM DATA",form.cleaned_data["news_Response"])

            currentParticipant = Participant.objects.get(user=request.user)
            currentParticipant.participantStatus = participantStatusDict["quizTask"]
            news_response, created = NewsResponse.objects.get_or_create(
                participant=currentParticipant,
                news_Response=form.cleaned_data["news_Response"],
            )
            news_response.save()
            currentParticipant.save()

            # ts for logs
            participantViewLog = get_participantViewLog(currentParticipant)
            participantViewLog.quizTaskTS = datetime.now()
            participantViewLog.save()

            # save the newsresponse to node and change node status
            node.responseToNews = form.cleaned_data["news_Response"]
            node.responseToNewsTimestamp = datetime.now()
            node.status = "responseGiven"
            reduceTracker(_treatement)
            node.save()

            nodeID = node.nodeID if _treatement != "AdHocNodes" else None
            print(
                f"Treatment Log: {_treatement}, node={nodeID} completed by Participant: id={currentParticipant.id}, upi={currentParticipant.upiID} "
            )

            # get children if they exist, and change their status
            # refactor this stuff, put node children in model schema and get child ID form there
            if _treatement != "AdHocNodes":
                if node.child1ID:
                    print("yes child exist")
                    nextNode1 = Treatement.objects.get(nodeID=node.child1ID)
                    nextNode1.status = "awaitingParticipant"
                    # if _treatement in ("C0", "T2"):
                    #     nextNode1.participantTypeRequired = "left" if currentParticipant.democaticOpinions < 50 else "right"
                    nextNode1.save()
                    

                if node.child2ID:
                    nextNode2 = Treatement.objects.get(nodeID=node.child2ID)
                    nextNode2.status = "awaitingParticipant"
                    # if _treatement in ("C0", "T2"):
                    #     nextNode2.participantTypeRequired = "left" if currentParticipant.democaticOpinions < 50 else "right"
                    nextNode2.save()

            # redirect to a new URL:
            return HttpResponseRedirect("/quizTask/")
            # return HttpResponse("thanks for filling the news Response form!")
            

    if request.method == "GET":
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if (
                    participant.participantStatus
                    != participantStatusDict["newsResponse"][0]
                ) and (
                    participant.newsStatus != participantStatusDict["newsResponse"][1]
                ):
                    return HttpResponseRedirect("/surveyRouter/")

        form = NewsResponseForm()

        context_table = {
            "nodeID": [None],
            "participantNo": [],
            "affiliation": [None],
            "accuracy": [None],
            "timestamp": [None],
            "treatement": _treatement,
        }

        currentParticipant = get_current_participant(request)
        currentParticipantAffiliation = currentParticipant.democaticOpinions
        currentParticipantTreatment = currentParticipant.treatement
        print(f"currentParticipantAffiliation: {currentParticipantAffiliation}")
        print(f"currentParticipantTreatment: {currentParticipantTreatment}")
        if _treatement != "AdHocNodes":

            participant_id = Participant.objects.get(user=request.user).id
            node = Treatement.objects.get(participant=participant_id)
            print(node.nodeID)
            node_ID = node.nodeID

            print("in loop:")
            for i in range(len(node.nodeID) - 1):
                print(i)
                node_ID = node_ID[:-1]

                context_table["nodeID"].insert(0, node_ID)
                context_table["participantNo"].append(i + 1)

                node = Treatement.objects.get(nodeID=node_ID)
                node_data = None

                # Added by Ranjeet
                # if node.responseToNews == 1:
                #     node_data = "Yes"
                # elif node.responseToNews == 0:
                #     node_data = "No"

                context_table["accuracy"].insert(0, node.responseToNews)
                context_table["timestamp"].insert(0, node.responseToNewsTimestamp)

                context_table["affiliation"].insert(
                    0, node.participant.democaticOpinions
                )
        else:
            node_ID = None

        print("Context Table",context_table)
        print("Context accuracy",context_table['accuracy'])
        # print(nodeIDs, participantResponses, participantAffiliations)
    # if a GET (or any other method) we'll create a blank form
    return render(
        request=request,
        template_name="survey/newsResponse.html",
        context={
            "form": form,
            "context_table": context_table,
            "range": range(len(context_table["nodeID"])),
            "current_participant_affiliation": currentParticipantAffiliation,
            "current_participant_treatement": currentParticipantTreatment,
            "treeID": node_ID,
        },
    )



# added function for quiz task page
@login_required
@never_cache
def quizTask(request):

    if request.method == "GET":
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if participant.participantStatus != participantStatusDict["quizTask"]:
                    return HttpResponseRedirect("/surveyRouter/")
        form = QuizForm()

    if request.method == "POST":

        form = QuizForm(request.POST)

        # permissions-------------------------
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if participant.participantStatus != participantStatusDict["quizTask"]:
                    return HttpResponseRedirect("/surveyRouter/")
        # ------------------------------------------------

        if form.is_valid():
            participant = get_current_participant(request)
            quiz_response, created = Quiz.objects.get_or_create(
                participant=participant,
                q1=form.cleaned_data["q1"],
                q2=form.cleaned_data["q2"],
                q3=form.cleaned_data["q3"],
            )
            participant.participantStatus = participantStatusDict["earnings"]
            quiz_response.save()
            participant.save()
            # ts for logs
            participantViewLog = get_participantViewLog(participant)
            participantViewLog.earningsTS = datetime.now()
            participantViewLog.save()

            return HttpResponseRedirect("/earnings/")

    return render(
        request=request, template_name="survey/quizTask.html", context={"form": form}
    )


# added view for earning page
@never_cache
def earnings(request):

    # Added by Ranjeet
    if request.method == "POST":
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if participant.participantStatus != participantStatusDict["earnings"]:
                    return HttpResponseRedirect("/surveyRouter/")

            form = EarningForm(request.POST)
            if form.is_valid():
                participant = get_current_participant(request)
                participant.participantStatus = participantStatusDict["finish"]
                participant.save()
                # ts for logs
                participantViewLog = get_participantViewLog(participant)
                participantViewLog.earningsTS = datetime.now()
                participantViewLog.save()

                return HttpResponseRedirect("/finish/")
            
            
    if request.method == "GET":
        print(request)
        if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if participant.participantStatus != participantStatusDict["earnings"]:
                    return HttpResponseRedirect("/surveyRouter/")

                upi = participant.upiID
                participation_fee = 50
                quiz = 0
                accuracy = 0
                earnings = 0
                _treatement = participant.treatement
                Treatement = apps.get_model("survey", _treatement)
                node_ID = Treatement.objects.get(participant=participant.id).nodeID
                if _treatement != "AdHocNodes":
                    news_item = node_ID[0]
                else:
                    news_item = None

                # Added by Ranjeet
                form = EarningForm()

                # check if earnings were already calculated or not
                earnings_details, made = Earnings.objects.get_or_create(upi=upi)
                if made:
                    # calculate earnings
                    num = random.randint(1, 100000) / 100000

                    nr = NewsResponse.objects.get(participant=participant).news_Response

                    print(f"news item: {news_item}")
                    print(f"nr item: {nr}")
                    print(f"node ID: {node_ID}")
                    print("num:", num)
                    if news_item == "A" or news_item == "B" or news_item == None:
                        # if post is inaccurate
                        prediction_error = (nr) / 100
                        print("post is inaccurate",prediction_error)
                    else:
                        # if post is accurate
                        prediction_error = (100 - nr) / 100
                        print("post is accurate",prediction_error)

                    # if prediction_error**2 < num:
                    #     accuracy += 200
                    if nr == False:
                        accuracy = 200

                    quiz_answers = Quiz.objects.get(participant=participant)
                    if quiz_answers.q1 == 2:
                        quiz += 50
                    if quiz_answers.q2 == 8:
                        quiz += 50
                    if quiz_answers.q3 == 2:
                        quiz += 50

                    earnings = quiz + accuracy + participation_fee
                    participant.totalEarnings = earnings
                    participant.save()

                    earnings_details.total = earnings
                    earnings_details.quiz = quiz
                    earnings_details.bonus = accuracy
                    earnings_details.pe = prediction_error
                    earnings_details.random_num = num
                    earnings_details.save()

                # if earnings were already calculated
                else:
                    earnings = earnings_details.total
                    quiz = earnings_details.quiz
                    accuracy = earnings_details.bonus

                # check if everything was already saved or not
                everything, created = Everything.objects.get_or_create(
                    participant=participant
                )
                print(f"created: {created}")
                # save only if everything is new
                if created:
                    tm = participant.treatement
                    democratic1 = DemocraticOpinion1.objects.get(
                        participant=participant
                    )
                    democratic2 = DemocraticOpinion2.objects.get(
                        participant=participant
                    )
                    quiz_a = Quiz.objects.get(participant=participant)
                    everything.news_source = democratic1.news_source
                    everything.affiliation = democratic1.affiliation
                    everything.democratic_Opinion = democratic1.democratic_Opinion
                    everything.age = democratic2.age
                    everything.gender = democratic2.gender
                    everything.religion = democratic2.religion
                    everything.state = democratic2.state
                    everything.district = democratic2.district
                    everything.highschool = democratic2.highschool
                    everything.edu_level = democratic2.edu_level
                    everything.course = democratic2.course
                    everything.checker = democratic2.checker
                    everything.voted = democratic2.voted
                    everything.social_media_apps = democratic2.social_media_apps
                    everything.time_spent = democratic2.time_spent
                    # everything.sources = democratic2.sources
                    everything.source_social_media = democratic2.source_social_media
                    everything.source_news_channels = democratic2.source_news_channels
                    everything.source_online_news_blogs = democratic2.source_online_news_blogs
                    everything.source_newspapers = democratic2.source_newspapers
                    everything.sm_other = democratic2.sm_other
                    everything.tv_other = democratic2.tv_other
                    everything.onp_other = democratic2.onp_other
                    everything.np_other = democratic2.np_other
                    everything.news_Response = NewsResponse.objects.get(
                        participant=participant
                    ).news_Response
                    everything.q1 = quiz_a.q1
                    everything.q2 = quiz_a.q2
                    everything.q3 = quiz_a.q3
                    everything.nodeID = node_ID if tm != "AdHocNodes" else "None"
                    everything.treatment = tm
                    everything.news_item = news_item if news_item != None else "A"
                    everything.save()

        return render(
            request=request,
            template_name="survey/earnings.html",
            context={
                "accuracy": accuracy,
                "earnings": earnings,
                "participation_fee": participation_fee,
                "quiz": quiz,
                "upi": upi,
                "form": form
            },
        )


def lastSeen(request):

    print(request.user)
    if request.method == "GET":
        try:
            participant = get_current_participant(request)
        except Exception as e:
            print("problem at last seen")
        else:
            participant.lastSeen = timezone.now()
            participant.save()
        finally:
            return HttpResponse()


# Added by Ranjeet
@login_required
@never_cache
def finishPage(request):
    # take to finish page
    if ROUTING_PERMISSIONS == True:
            try:
                participant = get_current_participant(request)
            except:
                print("exception happened")
            else:
                if participant.participantStatus != participantStatusDict["finish"]:
                    return HttpResponseRedirect("/surveyRouter/")
    return HttpResponse("Thank you for taking the survey, it’s submitted. You can now close the tab")



# Added by Ranjeet
@login_required
@never_cache
def kickOutPage(request):
    # took too long
    if request.method == "GET":
        try:
            participant = get_current_participant(request)
        except Exception as e:
            print("problem at kickOut page")
        else:
            participant.lastSeen = timezone.now()
            participant.totalEarnings = 0
            participant.save()

    return HttpResponse("Sorry No spots left")

# Added by Ranjeet
@login_required
@never_cache
def endOfSurvey(request):
    # took too long
    return HttpResponse("Sorry you took too long to answer")

# Added by Ranjeet
def sessionNotAvailable(request):
    # nodes are not available
    return HttpResponse("Waiting for the admin to start the session")


@login_required
@never_cache
def noSpotsAvailable(request):
    # early kick outs
    return HttpResponse(
        """
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <!-- Bootstrap CSS -->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
                integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
            </head>
            <body>
                <div class="container mt-3">
                    <p class="lead">
                        Our allocation algorithm randomly picks people based on suitability for the survey. Unfortunately, all the spots for today's session fitting your profile have already been taken. We will write to you if we have more sessions in the future. You can close this tab on your browser now and exit.
                    </p>
                </div>
            </body>
        </html>
        """
    )


# Added by Ranjeet
@login_required
def startStopSession(request):
    all_active = Treatment.objects.all().values_list('isActive')
    if False in [i[0] for i in all_active]:
        Treatment.objects.all().update(isActive=True, updated_at=datetime.now())
    else:
        Treatment.objects.all().update(isActive=False,updated_at=datetime.now())

    modal_id = 'survey/treatment'
    admin_url = reverse('admin:index')
    modal_url = f'{admin_url}{modal_id}'
    return redirect(modal_url)


from .dbSchema import makeTreeNode, makeInteractionTreeNode2, makeInteractionTreeNode
@login_required
def insertDataInTable(request):
    if request.method == "POST":
        print(request.POST)
        _treatment = request.POST.get('table_name')
        Treatement = apps.get_model(app_label="survey", model_name=_treatment)
        depth = int(request.POST.get("Depth"))
        number = int(request.POST.get("Number"))
        Treatement.objects.all().delete()
        leftSpots, centreSpots, rightSpots, noPreferenceSpots = 0,0,0,0,
        
        if _treatment in ("T2", "C0"):
            makeInteractionTreeNode(Treatement, "A", depth, number)
            makeInteractionTreeNode2(Treatement, "B", depth, number)
        else:
            makeTreeNode(Treatement, "A", depth, number)
            makeTreeNode(Treatement, "B", depth, number)

        print()
        countOfNodes = Treatement.objects.all().count()
        if _treatment == "C0":
            noPreferenceSpots = countOfNodes
        elif _treatment == "T2":
            leftSpots = countOfNodes//2
            rightSpots = countOfNodes//2
        elif _treatment in ("T1_L", "C0_L"):
            leftSpots = countOfNodes
        else:
            rightSpots = countOfNodes

        tracker = Tracker2.objects.filter(treatementName=_treatment)
        if tracker.exists():
            tracker.delete()

        print(leftSpots,centreSpots,rightSpots,noPreferenceSpots)
        Tracker2.objects.create(
            treatementName = _treatment,
            leftSpots = leftSpots,
            centreSpots = centreSpots,
            rightSpots = rightSpots,
            noPreferenceSpots = noPreferenceSpots
        )
        print("Inserted the data in",Treatement)
        modal_id = 'survey/treatment'
        admin_url = reverse('admin:index')
        modal_url = f'{admin_url}{modal_id}'
        return redirect(modal_url)

import io, csv
from zipfile import ZipFile
def downloadCSV(request):
    if request.method == "GET":
        print("INSIDE")
        treatment = Treatment.objects.filter(isActive=True)
        if treatment.exists():
            session_start_time = treatment.first().updated_at
            print(session_start_time)
            participants = Participant.objects.filter(updated_at__range=(session_start_time,datetime.now()))
            print(participants)

            everythings = Everything.objects.filter(updated_at__range=(session_start_time,datetime.now())).values()
            
            with open("Earning_data.csv",'w', newline="") as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(["totalEarnings","upiID","participantStatus"])
                for participant in participants:
                    data = [participant.totalEarnings,participant.upiID,participant.participantStatus]
                    print(data)
                    wr.writerow(data)

            with open("Responses_data.csv",'w', newline="") as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                first = True
                for everything in everythings:
                    everything.pop('updated_at')
                    if first:
                        wr.writerow(everything)
                        first = False
                    wr.writerow(everything.values())
            byte = io.BytesIO()

            zf = ZipFile(byte, 'w')
            zf.write("Earning_data.csv")
            zf.write("Responses_data.csv")
            zf.close()

            def strfTime(dateData):
                return str(dateData.strftime("%m/%d/%Y-%H:%M:%S"))
            session_start_time = strfTime(session_start_time)
            now_time = strfTime(datetime.now())
            print(session_start_time, now_time)
            resp = HttpResponse(
                byte.getvalue(), content_type="application/x-zip-compressed")
            resp['Content-Disposition'] = f'attachment; filename={str(session_start_time)}-to-{str(now_time)}.zip'
            return resp

            # with open("Responses_data.csv") as myfile:
            #     response = HttpResponse(myfile, content_type='text/csv')
            #     response['Content-Disposition'] = 'attachment; filename=stockitems_misuper.csv'
            #     return response
        
        modal_id = 'survey/treatment'
        admin_url = reverse('admin:index')
        modal_url = f'{admin_url}{modal_id}'
        return redirect(modal_url)