from asyncio.log import logger
import random
from datetime import timedelta, datetime

from django.apps import apps
from django.utils import timezone
from .models import Tracker2, Participant
from .utils import get_participantViewLog, get_current_participant

def checkTrackerForTreatementAndOpenSpots(currentParticipant):
    """still doing this"""
    """Takes in the Participant objects and checks if based on their 
    democratic opinion spots and treatements are available.
    If no returns None
    If yes returns 2 lists:[treatemt names][spots available in it]
    [T1_L, C0][6, 9]

    Args:
        currentParticipant ([Particpant]): the current Participant object

    Returns:
        [treatement name][spots available in it]: [description]
    """
    if currentParticipant.democaticOpinions < 50:
        
        spots = Tracker2.objects.filter(openLeftSpots__gt = 0) | Tracker2.objects.filter(noPreferenceSpots__gt=0)

        
        if len(spots)==0:                    
            return None 
        else:
            treatements = [i.treatementName for i in spots]
            leftSpots = [i.leftSpots if i.leftSpots is not None else  i.noPreferenceSpots for i in spots]
            return treatements , leftSpots


    if currentParticipant.democaticOpinions > 50:
        spots = Tracker2.objects.filter(rightSpots__gt = 0) | Tracker2.objects.filter(noPreferenceSpots__gt=0)                                     
        
        if len(spots)==0:                    
            return None 
        else:
            treatements = [i.treatementName for i in spots]
            rightSpots = [i.rightSpots if i.rightSpots is not None else  i.noPreferenceSpots for i in spots]
            return treatements , rightSpots 
    
    if currentParticipant.democaticOpinions == 50:
        spots = Tracker2.objects.filter(centreSpots__gt = 0) | Tracker2.objects.filter(noPreferenceSpots__gt=0)
        if len(spots)==0:                    
            return None 
        else:
            treatements = [i.treatementName for i in spots]
            centreSpots = [i.centreSpots if i.centreSpots is not None else  i.noPreferenceSpots for i in spots]
            return treatements , centreSpots  



def checkTrackerForTreatementAndSpots(currentParticipant):
    """Takes in the Participant objects and checks if based on their
    democratic opinion spots and treatements are available.
    If no returns None
    If yes returns 2 lists:[treatemt names][spots available in it]
    [T1_L, C0][6, 9]
    Args:
        currentParticipant ([Particpant]): the current Participant object
    Returns:
        [treatement name][spots available in it]: [description]
    """
    if currentParticipant.democaticOpinions < 50:

        spots = Tracker2.objects.filter(leftSpots__gt=0) | Tracker2.objects.filter(
            noPreferenceSpots__gt=0
        )

        if len(spots) == 0:
            return None
        else:
            treatements = [i.treatementName for i in spots]
            leftSpots = [
                i.leftSpots if i.leftSpots is not None else i.noPreferenceSpots
                for i in spots
            ]
            return treatements, leftSpots

    if currentParticipant.democaticOpinions > 50:
        spots = Tracker2.objects.filter(rightSpots__gt=0) | Tracker2.objects.filter(
            noPreferenceSpots__gt=0
        )
        print("spots",spots)
        if len(spots) == 0:
            return None
        else:
            treatements = [i.treatementName for i in spots]
            rightSpots = [
                i.rightSpots if i.rightSpots is not None else i.noPreferenceSpots
                for i in spots
            ]
            return treatements, rightSpots

    if currentParticipant.democaticOpinions == 50:
        spots = Tracker2.objects.filter(centreSpots__gt=0) | Tracker2.objects.filter(
            noPreferenceSpots__gt=0
        )
        if len(spots) == 0:
            return None
        else:
            treatements = [i.treatementName for i in spots]
            centreSpots = [
                i.centreSpots if i.centreSpots is not None else i.noPreferenceSpots
                for i in spots
            ]
            return treatements, centreSpots


def get_firstParticipant():
    # edit this to have last seen = > 2 second
    try:
        firstParticipant = Participant.objects.filter(
            participantStatus="awaitingToBecomeANode",
            lastSeen__gt=timezone.now() - timedelta(seconds=6),
        ).order_by("democaticOpinionResponseTime")[0]
        print(f"first participant is {firstParticipant}")
        return firstParticipant
    except Exception as e:
        print(e)
        print("exception happened while getting first participant")
        return None


def checkIfFirstParticipant(currentParticipant):
    firstParticipant = get_firstParticipant()

    if firstParticipant == currentParticipant:
        return True
    else:
        # currentParticipant.
        return False


def selectTreatement(spots):
    treatement = random.choice(spots[0])
    return treatement


def isUnderThreshold(spots, currentParticipant):
    # democaticOpinions = currentParticipant.democaticOpinions
    # print(democaticOpinions)
    # if democaticOpinions < 50:
    #     # participantNumber
    #     participants = Participant.objects.filter(
    #         participantStatus="awaitingToBecomeANode",
    #         democaticOpinions__lt=50,
    #         lastSeen__gt=timezone.now() - timedelta(seconds=6),
    #     ).order_by("democaticOpinionResponseTime")

    #     print(participants)
    # if democaticOpinions == 50:
    #     # participantNumber
    #     participants = Participant.objects.filter(
    #         participantStatus="awaitingToBecomeANode",
    #         democaticOpinions=50,
    #         lastSeen__gt=timezone.now() - timedelta(seconds=6),
    #     ).order_by("democaticOpinionResponseTime")

    # if democaticOpinions > 50:
    #     # participantNumber
    #     participants = Participant.objects.filter(
    #         participantStatus="awaitingToBecomeANode",
    #         democaticOpinions__gt=50,
    #         lastSeen__gt=timezone.now() - timedelta(seconds=6),
    #     ).order_by("democaticOpinionResponseTime")

    # print(f"participants query set : {participants}")
    # for i, val in enumerate(participants):
    #     if currentParticipant == val:
    #         currentParticipantNumber = i
    #         print(f"{currentParticipant.upiID}'s index is {i}")

    # limit = sum(spots[1])
    # print(f"limit is {limit}")

    # if currentParticipantNumber:
    #     if limit + 10 >= currentParticipantNumber:
    #         print(f"{currentParticipant.upiID} can stay")
    #         return True
    #     else:
    #         print(f"sorry {currentParticipant.upiID} exceeds the limit")
    #         return False
    # else:
    #     return True
    return True


def openNodesT2(_treatement,politicalLeaning):
    Treatement = apps.get_model(app_label="survey", model_name=_treatement)

    try:
        # Added by Ranjeet
        openNode = Treatement.objects.select_for_update().filter(status="awaitingParticipant", participantTypeRequired=politicalLeaning)[0]
        return openNode
    except Exception as e:
        return None

def openNodes(_treatement):
    Treatement = apps.get_model(app_label="survey", model_name=_treatement)

    try:
        # Added by Ranjeet
        openNode = Treatement.objects.select_for_update().filter(status="awaitingParticipant")[0]
        return openNode
    except Exception as e:
        return None


def actually_allot_node(openNode, currentParticipant, treatement):
    # openNode = "ABA"
    openNode.participant = currentParticipant
    openNode.status = "awaitingParticipantResponse"
    openNode.save()
    currentParticipant.treatement = treatement
    currentParticipant.participantStatus = "isANode"
    if treatement == "AdHocNodes":
        # currentParticipant.newsStatus = "onNewsResponse"
        currentParticipant.newsStatus = "onNewsInfo"
    else:
        currentParticipant.newsStatus = "onNewsInfo"
        
    currentParticipant.newsResponseInfoTimeLimit=timezone.now() + timedelta(seconds=300)
    # currentParticipant.newsResponseTimeLimit = timezone.now() + timedelta(seconds=45)
    currentParticipant.save()
    participantViewLog = get_participantViewLog(currentParticipant)                
    participantViewLog.newsResponseInfoTS = datetime.now()
    participantViewLog.save()

    nodeID = openNode.nodeID if treatement != "AdHocNodes" else None
    print(f"Treatment Log: {treatement}, node={nodeID} occupied by Participant: id={currentParticipant.id}, upi={currentParticipant.upiID} ")


def deadNodes(_treatement):
    #buggyy coz of this
    Treatement = apps.get_model(app_label="survey", model_name=_treatement)
    
    if _treatement == "AdHocNodes":
        return None

    try:
        deadNode = Treatement.objects.filter(status="awaitingParticipantResponse")[0]
        deadNodeTimeLimit1 = deadNode.participant.newsResponseInfoTimeLimit
        deadNodeTimeLimit2 = deadNode.participant.newsResponseTimeLimit
        deadParticipant = deadNode.participant

        if deadNodeTimeLimit2:
            if timezone.now() > deadNodeTimeLimit2:
                print("there is a dead node")
                print(f"Treatment Log: {_treatement}, node={deadNode.nodeID} reset and Participant: id={deadParticipant.id}, upi={deadParticipant.upiID} ")

                return deadNode, deadParticipant
                           
        else:
            if timezone.now() > deadNodeTimeLimit1:
                print("there is a dead node")
                print(f"Treatment Log: {_treatement}, node={deadNode.nodeID} reset and Participant: id={deadParticipant.id}, upi={deadParticipant.upiID} ")

                return deadNode, deadParticipant
            # return deadNode, deadParticipant

        
    except Exception as e:
        return None


def resetDeadNodeAndParticipant(deadNodeAndParticipant):
    deadNode = deadNodeAndParticipant[0]
    deadParticipant = deadNodeAndParticipant[1]
    deadNode.status = "awaitingParticipant"
    deadNode.participant = None
    deadParticipant.status = "becameADeadNode"
    deadNode.save()
    deadParticipant.save()
    

