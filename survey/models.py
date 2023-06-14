from django.contrib.auth.models import AbstractUser
from django.db import models


# class User(AbstractBaseUser):
#     username = models.CharField(max_length=60, unique=True)
#     USERNAME_FIELD = 'username'
class User(AbstractUser):
    pass


# Create your models here.
class Participant(models.Model):
    user = models.OneToOneField(
        User, related_name="logged_in_user", on_delete=models.CASCADE, default=None
    )
    session = models.CharField(max_length=500, default=None, null=True, unique=False)
    # unique = True in production
    upiID = models.CharField(max_length=200, null=True, unique=True)
    REQUIRED_FIELDS = ["upiID"]
    democaticOpinions = models.IntegerField(blank=False, null=True, default=0)
    allotmentTriesAfterBecomingFirstParticipant = models.IntegerField(
        blank=False, null=True, default=None
    )
    democaticOpinionResponseTime = models.DateTimeField(
        blank=False, default=None, null=True
    )
    TREATEMENT_CHOICES = [
        ("C0", "C0"),
        ("T1_L", "T1_L"),
        ("T1_R", "T1_R"),
        ("Nope", "Nope"),
    ]
    treatement = models.CharField(
        max_length=500,
        choices=TREATEMENT_CHOICES,
        default="Nope",
    )
    participantStatus = models.CharField(
        max_length=500, blank=False, null=True, default="notANode"
    )

    newsStatus = models.CharField(max_length=500, blank=False, null=True, default="")
    # 1, 2: "awaitingUPI", 3:"awaitingDemocraticOpinion" 4:"awaitingToBecomeANode"
    # 5: IsANode #6: timedOut #earlyGoodbye #surveyCompleted
    lastSeen = models.DateTimeField(blank=False, default=None, null=True)
    newsResponseInfoTimeLimit = models.DateTimeField(
        blank=False, default=None, null=True
    )
    newsResponseTimeLimit = models.DateTimeField(blank=False, default=None, null=True)

    triesCheckOpenNodes = models.IntegerField(default=0)
    # awaitingToBecomeANode #IsANode #timedOut #surveyCompleted
    totalEarnings = models.IntegerField(default=0)

    def __str__(self):
        return self.upiID


class ParticipantViewLogs(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    democraticOpinion1TS = models.DateTimeField(blank=False, default=None, null=True)
    democraticOpinion2TS = models.DateTimeField(blank=False, default=None, null=True)
    newsAccuracyTaskTS = models.DateTimeField(blank=False, default=None, null=True)
    waitingRoomNewTS = models.DateTimeField(blank=False, default=None, null=True)
    newsResponseInfoTS = models.DateTimeField(blank=False, default=None, null=True)
    newsResponseTS = models.DateTimeField(blank=False, default=None, null=True)
    quizTaskTS = models.DateTimeField(blank=False, default=None, null=True)
    earningsTS = models.DateTimeField(blank=False, default=None, null=True)

    noSpotsAvailableTS = models.DateTimeField(blank=False, default=None, null=True)


# model to store earnings details without participnt id linked to it
class Earnings(models.Model):
    total = models.IntegerField(default=0)
    quiz = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    upi = models.CharField(max_length=200, null=True, unique=True)
    pe = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    random_num = models.DecimalField(max_digits=6, decimal_places=5, default=0)


# model to save everything as wanted in one table
class Everything(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    news_source = models.CharField(max_length=800, blank=False, null=True, default="")
    affiliation = models.BooleanField(blank=False, null=True, default=None)
    democratic_Opinion = models.CharField(
        max_length=800, blank=False, null=True, default=""
    )
    age = models.IntegerField(blank=False, null=True, default=None)
    gender = models.CharField(max_length=800, blank=False, null=True, default="")
    religion = models.CharField(max_length=800, blank=False, null=True, default="")
    state = models.CharField(max_length=800, blank=False, null=True, default="")
    district = models.CharField(max_length=800, blank=False, null=True, default="")
    highschool = models.CharField(max_length=800, blank=False, null=True, default="")
    edu_level = models.CharField(max_length=800, blank=False, null=True, default="")
    course = models.CharField(max_length=800, blank=False, null=True, default="")
    checker = models.CharField(max_length=800, blank=False, null=True, default="")
    voted = models.BooleanField(blank=False, null=True, default=None)
    social_media_apps = models.CharField(
        max_length=800, blank=False, null=True, default=""
    )
    time_spent = models.CharField(max_length=800, blank=False, null=True, default="")
    # sources = models.CharField(max_length=1000, blank=False, null=True, default="")
    source_social_media = models.CharField(max_length=150, blank=False, null=True, default="")
    source_news_channels = models.CharField(max_length=150, blank=False, null=True, default="")
    source_online_news_blogs = models.CharField(max_length=150, blank=False, null=True, default="")
    source_newspapers = models.CharField(max_length=150, blank=False, null=True, default="")
    sm_other = models.CharField(max_length=800, blank=True, null=True, default="")
    tv_other = models.CharField(max_length=800, blank=True, null=True, default="")
    onp_other = models.CharField(max_length=800, blank=True, null=True, default="")
    np_other = models.CharField(max_length=800, blank=True, null=True, default="")
    news_Response = models.BooleanField(blank=False, null=True, default=None)

    # news_Response = models.IntegerField(blank=False, null=True, default=None)
    q1 = models.IntegerField(blank=False, null=True, default=None)
    q2 = models.IntegerField(blank=False, null=True, default=None)
    q3 = models.IntegerField(blank=False, null=True, default=None)
    nodeID = models.CharField(max_length=50, null=True, default=None)
    treatment = models.CharField(max_length=500, null=True, default=None)
    news_item = models.CharField(max_length=500, null=True, default=None)


class DemocraticOpinion1(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    news_source = models.CharField(max_length=800, blank=False, null=True, default="")
    affiliation = models.BooleanField(blank=False, null=True, default=None)
    democratic_Opinion = models.CharField(
        max_length=800, blank=False, null=True, default=""
    )


class DemocraticOpinion2(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    age = models.IntegerField(blank=False, null=True, default=None)
    gender = models.CharField(max_length=800, blank=False, null=True, default="")
    religion = models.CharField(max_length=800, blank=False, null=True, default="")
    state = models.CharField(max_length=800, blank=False, null=True, default="")
    district = models.CharField(max_length=800, blank=False, null=True, default="")
    highschool = models.CharField(max_length=800, blank=False, null=True, default="")
    edu_level = models.CharField(max_length=800, blank=False, null=True, default="")
    course = models.CharField(max_length=800, blank=False, null=True, default="")
    checker = models.CharField(max_length=800, blank=False, null=True, default="")
    voted = models.BooleanField(blank=False, null=True, default=None)
    social_media_apps = models.CharField(
        max_length=800, blank=False, null=True, default=""
    )
    time_spent = models.CharField(max_length=800, blank=False, null=True, default="")
    # sources = models.CharField(max_length=1000, blank=False, null=True, default="")
    source_social_media = models.CharField(max_length=150, blank=False, null=True, default="")
    source_news_channels = models.CharField(max_length=150, blank=False, null=True, default="")
    source_online_news_blogs = models.CharField(max_length=150, blank=False, null=True, default="")
    source_newspapers = models.CharField(max_length=150, blank=False, null=True, default="")
    sm_other = models.CharField(max_length=800, blank=True, null=True, default="")
    tv_other = models.CharField(max_length=800, blank=True, null=True, default="")
    onp_other = models.CharField(max_length=800, blank=True, null=True, default="")
    np_other = models.CharField(max_length=800, blank=True, null=True, default="")


class NewsResponse(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    # Added by Ranjeet
    news_Response = models.BooleanField(blank=False, null=True, default=None)
    # news_Response = models.IntegerField(blank=False, null=True, default=None)


class Quiz(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, null=True, default=None, blank=True
    )
    q1 = models.IntegerField(blank=False, null=True, default=None)
    q2 = models.IntegerField(blank=False, null=True, default=None)
    q3 = models.IntegerField(blank=False, null=True, default=None)


class AllotmentLogs(models.Model):
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    triesCheckTracker = models.IntegerField(null=True, default=0)
    triesCheckFirstParticipant = models.IntegerField(null=True, default=0)
    triesCheckThreshold = models.IntegerField(null=True, default=0)
    triesSelectTreatement = models.IntegerField(null=True, default=0)
    triesCheckOpenNodes = models.IntegerField(null=True, default=0)
    triesCheckDeadNodes = models.IntegerField(null=True, default=0)
    triesResetDeadNodeAndParticipant = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.participant


class C0(models.Model):
    nodeID = models.CharField(max_length=50, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    participantTypeRequired = models.CharField(
        max_length=50, blank=True, default="left"
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)

    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=500, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=50, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID


class T1_L(models.Model):
    # only allow Left
    nodeID = models.CharField(max_length=150, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=50, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=150, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=150, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID


class T1_R(models.Model):
    # only allow Right
    nodeID = models.CharField(max_length=50, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=50, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=50, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID


class T2(models.Model):
    # interaction treatement
    nodeID = models.CharField(max_length=50, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    participantTypeRequired = models.CharField(
        max_length=50, blank=True, default="left"
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=50, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=50, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID


class AdHocNodes(models.Model):
    # interaction treatement

    nodeID = models.CharField(max_length=50, null=True, default="None")
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )

    # responseToNews = models.IntegerField(null=True, default=None)
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(
        max_length=50, blank=True, default="awaitingParticipantResponse"
    )
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven

    def __str__(self):
        return self.pk


class Tracker2(models.Model):
    treatementName = models.CharField(
        max_length=500, null=True, default=None, unique=True
    )
    leftSpots = models.IntegerField(null=True, default=None, blank=True)
    centreSpots = models.IntegerField(null=True, default=None, blank=True)
    rightSpots = models.IntegerField(null=True, default=None, blank=True)
    noPreferenceSpots = models.IntegerField(null=True, default=None, blank=True)

    def __str__(self):
        return self.treatementName

# Added by Ranjeet
# Added new table to control the node is active or not
class Treatment(models.Model):
    treatmentNodeName = models.CharField(
        max_length=50, null=False, unique=True
    )
    isActive = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.treatmentNodeName
    

# Added by Ranjeet

class C0_L(models.Model):
    # only allow Left
    nodeID = models.CharField(max_length=50, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=50, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=50, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID


class C0_R(models.Model):
    # only allow Right
    nodeID = models.CharField(max_length=50, null=True, default=None, unique=True)
    participant = models.OneToOneField(
        Participant, on_delete=models.SET_DEFAULT, null=True, default=None, blank=True
    )
    # Added by Ranjeet
    responseToNews = models.BooleanField(blank=False, null=True, default=None)
    # responseToNews = models.IntegerField(null=True, default=None)
    responseToNewsTimestamp = models.DateTimeField(blank=False, default=None, null=True)
    status = models.CharField(max_length=50, blank=True, default="outOfService")
    # outOfService #awaitingParticipant #awaitingParticipantResponse #responseGiven
    child1ID = models.CharField(max_length=50, null=True, blank=True, unique=True)
    child2ID = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return self.nodeID