import json

from time import sleep


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

# Create your views here.


from survey.models import Participant
from .models import User, Participant, C0


from django.contrib.auth import get_user_model


import asyncio

from channels.db import database_sync_to_async


User = get_user_model()

# not using, use AsyncConsumer
class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        def allotNodeConsumer(self):
            self.user = self.scope["user"]
            self.session = self.scope["session"]
            print(f"from consumer:{self.user}, {self.session}")

            # 3 DB access (have to be syncronous)
            openNodes = C0.objects.filter(status="awaitingParticipant")  # 1
            openParticipants = Participant.objects.filter(
                participantStatus="awaitingToBecomeANode"
            ).order_by(
                "democaticOpinionResponseTime"
            )  # 2

            currentParticipant = Participant.objects.get(user=self.user)  # 3

            print(f"task on behalf of {currentParticipant}")

            if len(openNodes) > 0:
                print("Open nodes exist")
                if openParticipants[0] == currentParticipant:
                    print(f"and {currentParticipant} is the first in queu.")

                    self.send(json.dumps({"message": "Refresh"}))
                    print(
                        f"{self.user} is Now a Node at {openNodes[0].nodeID}, you can refresh the page"
                    )
                    sleep(10)
                    return 1
                else:
                    print(f"and {currentParticipant} is NOT first in queue")
            elif len(openNodes) == 0:
                print("no open nodes yet")
            return 0

        # allotNodeConsumer(self)


class WSConsumerAsync(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        self.session = self.scope["session"]
        if not self.scope["user"].is_authenticated:
            print(f"Something went wrong:{self.user}")
            print(self.session, self.user)

        
        

        # loop = asyncio.get_event_loop()
        # asyncio.ensure_future(my_sleep_func())

        # print(loop)

        # 1. keep checking if currentParticipant is the fist in queue, eveny 2 seconds

        # get current particiapnt
        self.currentParticipant = await self.get_currentParticipant(self.user)
        # get first in queue
        self.firstParticipant = await self.get_firstParticipant()

        while self.currentParticipant != self.firstParticipant:
            await asyncio.sleep(2)
            print(f"{self.currentParticipant} is NOT first in queue")
            self.firstParticipant = await self.get_firstParticipant()
        print(f"{self.currentParticipant} is first in queue ")

        # 2. When current participant is the first participant, check for the first open Node
        self.openNode = await self.get_openNode()
        while self.openNode is None:
            await asyncio.sleep(2)
            print(f"no open nodes yet")
            self.openNode = await self.get_openNode()
        print(f"open node is {self.openNode}")

        # 3. when open node is found, actually allot node
        await self.actually_allot_node(self.openNode, self.currentParticipant)

        # 4. send a "Refresh" message to the frontend, it will look at it and refresh the page
        await self.send(json.dumps({"message": "Refresh"}))
        

    @database_sync_to_async
    def get_firstParticipant(self):
        #edit this to have last seen = > 2 second 
        return Participant.objects.filter(
            participantStatus="awaitingToBecomeANode"
        ).order_by("democaticOpinionResponseTime")[0]

    @database_sync_to_async
    def get_currentParticipant(self, userPerson):
        return Participant.objects.get(user=self.user)

    @database_sync_to_async
    def get_openNode(self):
        try:
            openNode = C0.objects.filter(status="awaitingParticipant")[0]
            return openNode
        except Exception as e:
            return None

    @database_sync_to_async
    def actually_allot_node(self, openNode, currentParticipant):
        openNode.participant = currentParticipant
        openNode.status = "awaitingParticipantResponse"
        openNode.save()
        currentParticipant.participantStatus = "IsANode"
        currentParticipant.save()
        return 0
