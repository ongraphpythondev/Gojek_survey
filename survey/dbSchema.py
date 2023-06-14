import random
import secrets
from datetime import timedelta

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from survey.models import Participant

from .decorators import *
from .models import C0, T1_L, T1_R, T2, Participant, Tracker2, User, Earnings, Treatment, C0_L, C0_R
from .utils import *
from .utils_allotmentLogic import *


@login_required
def createDatabase(request):
    Treatement = T2
    print(Treatement.objects.all())
    if request.method == "GET":
        if not request.user.is_superuser:
            return HttpResponse("You dont have permissions to view this page")
        Treatement.objects.all().delete()
        Treatement.objects.create(
            nodeID="A",
            participant=None,
            responseToNews=None,
            status="awaitingParticipant",
            child1ID="AA",
            child2ID="AB",
        )
        Treatement.objects.create(
            nodeID="AA",
            participant=None,
            responseToNews=None,
            status="outOfService",
            child1ID="AAA",
            child2ID="AAB",
        )
        Treatement.objects.create(
            nodeID="AB",
            participant=None,
            responseToNews=None,
            status="outOfService",
            child1ID="ABA",
            child2ID="ABB",
        )
        Treatement.objects.create(
            nodeID="AAA",
            participant=None,
            responseToNews=None,
            status="outOfService",
        )
        Treatement.objects.create(
            nodeID="AAB",
            participant=None,
            responseToNews=None,
            status="outOfService",
        )
        Treatement.objects.create(
            nodeID="ABA",
            participant=None,
            responseToNews=None,
            status="outOfService",
        )
        Treatement.objects.create(
            nodeID="ABB",
            participant=None,
            responseToNews=None,
            status="outOfService",
        )

        Treatement.objects.create(
            nodeID="B",
            participant=None,
            responseToNews=None,
            status="awaitingParticipant",
            participantTypeRequired="left",
        )
        Treatement.objects.create(
            nodeID="BA",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="right",
        )
        Treatement.objects.create(
            nodeID="BB",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="right",
        )
        Treatement.objects.create(
            nodeID="BAA",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="left",
        )
        Treatement.objects.create(
            nodeID="BAB",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="left",
        )
        Treatement.objects.create(
            nodeID="BBA",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="left",
        )
        Treatement.objects.create(
            nodeID="BBB",
            participant=None,
            responseToNews=None,
            status="outOfService",
            participantTypeRequired="left",
        )
    return HttpResponse("database created")


@transaction.atomic
@login_required
def fillSchema(request):
    print(request.user)

    if request.method == "GET":
        if not request.user.is_superuser:
            return HttpResponse("You dont have permissions to view this page")

        returnString = ""

        def makeTreeNode(Treatement, nodeID, depth, stopSplittingAt):

            noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
            child1ID = nodeID + "A" if len(nodeID) <= depth else None
            child2ID = (
                nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
            )
            status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
            try:
                with transaction.atomic():
                    Treatement.objects.create(
                        nodeID=nodeID,
                        participant=None,
                        responseToNews=None,
                        status=status,
                        child1ID=child1ID,
                        child2ID=child2ID,
                    )
            except Exception as e:
                print(e)

            else:

                print("made node")

            if child1ID:
                makeTreeNode(Treatement, child1ID, depth, stopSplittingAt)
            if child2ID:
                makeTreeNode(Treatement, child2ID, depth, stopSplittingAt)

            else:
                return child1ID, child2ID

        def makeInteractionTreeNode(
            Treatement, nodeID, depth, stopSplittingAt, participantTypeRequired=None
        ):
            """
            first node is a right node
            """
            noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
            child1ID = nodeID + "A" if len(nodeID) <= depth else None
            child2ID = (
                nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
            )
            status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
            participantTypeRequired = "left" if len(nodeID) % 2 == 0 else "right"

            try:
                Treatement.objects.create(
                    nodeID=nodeID,
                    participant=None,
                    responseToNews=None,
                    status=status,
                    child1ID=child1ID,
                    child2ID=child2ID,
                    participantTypeRequired=participantTypeRequired,
                )
            except Exception as e:
                print(e)
            else:
                print(
                    f"Created node {nodeID} in {str(Treatement)} of type {participantTypeRequired}\n"
                )

            if child1ID:
                makeInteractionTreeNode(
                    Treatement,
                    child1ID,
                    depth,
                    stopSplittingAt,
                    participantTypeRequired,
                )
            if child2ID:
                makeInteractionTreeNode(
                    Treatement,
                    child2ID,
                    depth,
                    stopSplittingAt,
                    participantTypeRequired,
                )

            else:
                return child1ID, child2ID

        def makeInteractionTreeNode2(
            Treatement, nodeID, depth, stopSplittingAt, participantTypeRequired=None
        ):
            """
            first node is a left node
            """
            noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
            child1ID = nodeID + "A" if len(nodeID) <= depth else None
            child2ID = (
                nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
            )
            status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
            participantTypeRequired = "right" if len(nodeID) % 2 == 0 else "left"

            try:
                Treatement.objects.create(
                    nodeID=nodeID,
                    participant=None,
                    responseToNews=None,
                    status=status,
                    child1ID=child1ID,
                    child2ID=child2ID,
                    participantTypeRequired=participantTypeRequired,
                )
            except Exception as e:
                print(e)
            else:
                print(
                    f"Created node {nodeID} in {str(Treatement)} of type {participantTypeRequired}\n"
                )

            if child1ID:
                makeInteractionTreeNode2(
                    Treatement,
                    child1ID,
                    depth,
                    stopSplittingAt,
                    participantTypeRequired,
                )
            if child2ID:
                makeInteractionTreeNode2(
                    Treatement,
                    child2ID,
                    depth,
                    stopSplittingAt,
                    participantTypeRequired,
                )

            else:
                return child1ID, child2ID

        # reset the db by deleting first
        C0.objects.all().delete()
        T1_L.objects.all().delete()
        T1_R.objects.all().delete()
        Tracker2.objects.all().delete()
        T2.objects.all().delete()
        Earnings.objects.all().delete()
        # Added by Ranjeet
        Treatment.objects.all().delete()
        C0_R.objects.all().delete()
        C0_L.objects.all().delete()

        # delete all participants as well
        Participant.objects.all().delete()

        makeTreeNode(T1_L, "A", 11, 1)
        makeTreeNode(T1_L, "B", 11, 1)

        Tracker2.objects.create(
            treatementName = "T1_L",
            leftSpots = 46,
            centreSpots = 0,
            rightSpots = 0,
            noPreferenceSpots = 0
        )

        makeTreeNode(T1_R, "A", 11, 1)
        makeTreeNode(T1_R, "B", 11, 1)

        Tracker2.objects.create(
            treatementName = "T1_R",
            leftSpots = 0,
            centreSpots = 0,
            rightSpots = 46,
            noPreferenceSpots = 0
        )

        try:
            with transaction.atomic():
                makeInteractionTreeNode(T2, "A", 11, 1)
                makeInteractionTreeNode2(T2, "B", 11, 1)
        except Exception as e:
            print(e)
        else:
            print("T2 created")

        Tracker2.objects.create(
            treatementName="T2",
            leftSpots=23,
            centreSpots=0,
            rightSpots=23,
            noPreferenceSpots=0,
        )

        # Added by Ranjeet
        # Treatment object Creating

        try:
            with transaction.atomic():
                makeInteractionTreeNode(C0, "A", 11, 1)
                makeInteractionTreeNode2(C0, "B", 11, 1)
        except Exception as e:
            print(e)
        else:
            print("T2 created")

        Tracker2.objects.create(
            treatementName="C0",
            leftSpots=0,
            centreSpots=0,
            rightSpots=0,
            noPreferenceSpots=46,
        )


        Treatment.objects.create(
            treatmentNodeName="C0"
        )
        Treatment.objects.create(
            treatmentNodeName="T2"
        )
        Treatment.objects.create(
            treatmentNodeName="T1_L"
        )
        Treatment.objects.create(
            treatmentNodeName="T1_R"
        )
        Treatment.objects.create(
            treatmentNodeName="C0_L"
        )
        Treatment.objects.create(
            treatmentNodeName="C0_R"
        )

        makeTreeNode(C0_L, "A", 11, 1)
        makeTreeNode(C0_L, "B", 11, 1)

        Tracker2.objects.create(
            treatementName="C0_L",
            leftSpots=46,
            centreSpots=0,
            rightSpots=0,
            noPreferenceSpots=0,
        )

        makeTreeNode(C0_R, "A", 11, 1)
        makeTreeNode(C0_R, "B", 11, 1)

        Tracker2.objects.create(
            treatementName="C0_R",
            leftSpots=0,
            centreSpots=0,
            rightSpots=46,
            noPreferenceSpots=0,
        )

        ####----- test Jun 8:
        # makeTreeNode(C0, "A", 1, 1)
        # makeTreeNode(C0, "B", 1, 1)

        # Tracker2.objects.create(
        #     treatementName="C0",
        #     leftSpots=0,
        #     centreSpots=0,
        #     rightSpots=0,
        #     noPreferenceSpots=6,
        # )

        # makeTreeNode(T1_L, "A", 1, 1)
        # makeTreeNode(T1_L, "B", 1, 1)

        # Tracker2.objects.create(
        #     treatementName="T1_L",
        #     leftSpots=6,
        #     centreSpots=0,
        #     rightSpots=0,
        #     noPreferenceSpots=0,
        # )
        # makeTreeNode(T1_R, "A", 1, 1)
        # makeTreeNode(T1_R, "B", 1, 1)

        # Tracker2.objects.create(
        #     treatementName="T1_R",
        #     leftSpots=0,
        #     centreSpots=0,
        #     rightSpots=6,
        #     noPreferenceSpots=0,
        # )

        # T2.objects.all().delete()

        # try:
        #     with transaction.atomic():
        #         makeInteractionTreeNode(T2, "A", 2, 1)
        #         makeInteractionTreeNode2(T2, "B", 2, 1)

        # except Exception as e:
        #     print(e)
        # else:
        #     print("T2 created")

        # Tracker2.objects.create(
        #     treatementName="T2",
        #     leftSpots=5,
        #     centreSpots=0,
        #     rightSpots=5,
        #     noPreferenceSpots=0,
        # )

        ##### to test adhocNodes

        # makeInteractionTreeNode(T2, "A", 2, 1)
        # makeInteractionTreeNode(T2, "B", 2, 1)

        # Tracker2.objects.create(
        #     treatementName="T2",
        #     leftSpots=4,
        #     centreSpots=0,
        #     rightSpots=6,
        #     noPreferenceSpots=0,
        # )
        print("Data is Inserted")
        return HttpResponse("a")



def makeTreeNode(Treatement, nodeID, depth, stopSplittingAt):

    noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
    child1ID = nodeID + "A" if len(nodeID) <= depth else None
    child2ID = (
        nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
    )
    status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
    try:
        with transaction.atomic():
            Treatement.objects.create(
                nodeID=nodeID,
                participant=None,
                responseToNews=None,
                status=status,
                child1ID=child1ID,
                child2ID=child2ID,
            )
    except Exception as e:
        print(e)

    else:

        print("made node", end=" ")

    if child1ID:
        makeTreeNode(Treatement, child1ID, depth, stopSplittingAt)
    if child2ID:
        makeTreeNode(Treatement, child2ID, depth, stopSplittingAt)

    else:
        return child1ID, child2ID

def makeInteractionTreeNode(
    Treatement, nodeID, depth, stopSplittingAt, participantTypeRequired=None
):
    """
    first node is a right node
    """
    noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
    child1ID = nodeID + "A" if len(nodeID) <= depth else None
    child2ID = (
        nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
    )
    status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
    participantTypeRequired = "left" if len(nodeID) % 2 == 0 else "right"

    try:
        Treatement.objects.create(
            nodeID=nodeID,
            participant=None,
            responseToNews=None,
            status=status,
            child1ID=child1ID,
            child2ID=child2ID,
            participantTypeRequired=participantTypeRequired,
        )
    except Exception as e:
        print(e)
    else:
        print(
            f"Created node {nodeID} in {str(Treatement)} of type {participantTypeRequired}\n"
        )

    if child1ID:
        makeInteractionTreeNode(
            Treatement,
            child1ID,
            depth,
            stopSplittingAt,
            participantTypeRequired,
        )
    if child2ID:
        makeInteractionTreeNode(
            Treatement,
            child2ID,
            depth,
            stopSplittingAt,
            participantTypeRequired,
        )

    else:
        return child1ID, child2ID

def makeInteractionTreeNode2(
    Treatement, nodeID, depth, stopSplittingAt, participantTypeRequired=None
):
    """
    first node is a left node
    """
    noOfChildren = 2 if len(nodeID) <= stopSplittingAt else 1
    child1ID = nodeID + "A" if len(nodeID) <= depth else None
    child2ID = (
        nodeID + "B" if noOfChildren == 2 and len(nodeID) <= depth else None
    )
    status = "awaitingParticipant" if len(nodeID) == 1 else "outOfService"
    participantTypeRequired = "right" if len(nodeID) % 2 == 0 else "left"

    try:
        Treatement.objects.create(
            nodeID=nodeID,
            participant=None,
            responseToNews=None,
            status=status,
            child1ID=child1ID,
            child2ID=child2ID,
            participantTypeRequired=participantTypeRequired,
        )
    except Exception as e:
        print(e)
    else:
        print(
            f"Created node {nodeID} in {str(Treatement)} of type {participantTypeRequired}\n"
        )

    if child1ID:
        makeInteractionTreeNode2(
            Treatement,
            child1ID,
            depth,
            stopSplittingAt,
            participantTypeRequired,
        )
    if child2ID:
        makeInteractionTreeNode2(
            Treatement,
            child2ID,
            depth,
            stopSplittingAt,
            participantTypeRequired,
        )

    else:
        return child1ID, child2ID
