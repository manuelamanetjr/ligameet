from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Sport(models.Model):
    SPORT_NAME = models.CharField(max_length=100)
    SPORT_RULES_AND_REGULATIONS = models.TextField()
    EDITED_AT = models.DateTimeField(default=timezone.now)
    IMAGE = models.ImageField(upload_to='sports_icon/', null=True, blank=True)
    
    def __str__(self):
        return self.SPORT_NAME

# set default to upcoming TODO
class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    EVENT_NAME = models.CharField(max_length=100)
    EVENT_DATE_START = models.DateTimeField()
    EVENT_DATE_END = models.DateTimeField()
    EVENT_LOCATION = models.CharField(max_length=255)
    EVENT_STATUS = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    EVENT_ORGANIZER = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')

    def __str__(self):
        return self.EVENT_NAME

class Participant(models.Model):
    PART_TYPE_CHOICES = (
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('referee', 'Referee'),
        ('spectator', 'Spectator'),
    )
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    PART_TYPE = models.CharField(max_length=10, choices=PART_TYPE_CHOICES)

    def __str__(self):
        return f"{self.USER_ID.username} - {self.PART_TYPE}"


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    WALLET_BALANCE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user} - {self.WALLET_BALANCE}"


class File(models.Model):
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    FILE_PATH = models.FileField(upload_to='files/')

    def __str__(self):
        return str(self.FILE_PATH)


class Team(models.Model):
    TEAM_NAME = models.CharField(max_length=100)
    TEAM_TYPE = models.CharField(max_length=50) #junior senior
    TEAM_SCORE = models.IntegerField(default=0)
    SPORT_ID = models.ForeignKey(Sport, on_delete=models.CASCADE)
    COACH_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    PLAYERS = models.ManyToManyField(User, related_name='teams', blank=True)  # confirmed players
    PENDING_PLAYERS = models.ManyToManyField(User, related_name='pending_teams', blank=True)  # pending players

    def approve_player(self, player):
        """Move player from pending to confirmed"""
        if player in self.PENDING_PLAYERS.all():
            self.PENDING_PLAYERS.remove(player)
            self.PLAYERS.add(player)
            self.save()

    def __str__(self):
        return self.TEAM_NAME

class TeamParticipant(models.Model):
    IS_CAPTAIN = models.BooleanField(default=False)
    PART_ID = models.ForeignKey(Participant, on_delete=models.CASCADE)
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['PART_ID', 'TEAM_ID'], name='unique_team_participant')
        ]

    def __str__(self):
        return f"{self.PART_ID} - {self.TEAM_ID}"


class TeamEvent(models.Model):
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)
    EVENT_ID = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['TEAM_ID', 'EVENT_ID'], name='unique_team_event')
        ]

    def __str__(self):
        return f"Team: {self.TEAM_ID.TEAM_NAME} - Event: {self.EVENT_ID.EVENT_NAME}"
    

class Match(models.Model):
    MATCH_TYPE = models.CharField(max_length=50) #casual official
    MATCH_CATEGORY = models.CharField(max_length=50) #CIVIRAA
    MATCH_SCORE = models.IntegerField(default=0)
    MATCH_DATE = models.DateTimeField()
    MATCH_STATUS = models.CharField(max_length=20)
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.MATCH_TYPE} - {self.TEAM_ID.TEAM_NAME} on {self.MATCH_DATE}"


class Subscription(models.Model):
    SUB_PLAN = models.CharField(max_length=50)
    SUB_DATE_STARTED = models.DateTimeField(default=timezone.now)
    SUB_DATE_END = models.DateTimeField()
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.USER_ID.username} - {self.SUB_PLAN} (Started: {self.SUB_DATE_STARTED})"
    

class TeamRegistrationFee(models.Model):
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)
    MATCH_ID = models.ForeignKey(Match, on_delete=models.CASCADE)
    REGISTRATION_FEE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    IS_PAID = models.BooleanField(default=False)

    def __str__(self):
        return f"Team: {self.TEAM_ID.TEAM_NAME} - Match: {self.MATCH_ID.MATCH_TYPE} - Paid: {self.IS_PAID}"
    

class SportsEvent(models.Model):
    EVENT_ID = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True)
    SPORTS_ID = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"Event: {self.EVENT_ID.EVENT_NAME} - Sport: {self.SPORTS_ID.SPORT_NAME}"


class TeamMatch(models.Model):
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)
    MATCH_ID = models.ForeignKey(Match, on_delete=models.CASCADE)
    IS_WINNER = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['TEAM_ID', 'MATCH_ID'], name='unique_team_match')
        ]

    def __str__(self):
        return f"Team: {self.TEAM_ID.TEAM_NAME} - Match: {self.MATCH_ID.MATCH_TYPE} - Winner: {self.IS_WINNER}"


class UserMatch(models.Model):
    MATCH_ID = models.ForeignKey(Match, on_delete=models.CASCADE)
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    TEAM_ID = models.ForeignKey(Team, on_delete=models.CASCADE)
    IS_WINNER = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['MATCH_ID', 'USER_ID'], name='unique_user_match')
        ]

    def __str__(self):
        return f"Match: {self.MATCH_ID.MATCH_TYPE} - User: {self.USER_ID.username} - Team: {self.TEAM_ID.TEAM_NAME} - Winner: {self.IS_WINNER}"


class VolleyballStats(models.Model):
    VB_STATS_PT_COUNT = models.IntegerField(default=0)
    VB_STATS_ASSIST = models.IntegerField(default=0)
    VB_STATS_BLOCK = models.IntegerField(default=0)
    VB_STATS_ERROR = models.IntegerField(default=0)
    VB_STATS_IS_MVP = models.BooleanField(default=False)
    VB_STATS_SET = models.IntegerField(default=0)
    PART_ID = models.ForeignKey(Participant, on_delete=models.CASCADE)
    MATCH_ID = models.ForeignKey(Match, on_delete=models.CASCADE)
    USER_MATCH_ID = models.ForeignKey(UserMatch, on_delete=models.CASCADE)

    def __str__(self):
        return f"Participant: {self.PART_ID.USER_ID.username} - Match: {self.MATCH_ID.MATCH_TYPE} - MVP: {self.VB_STATS_IS_MVP}"


class UserRegistrationFee(models.Model):
    USER_MATCH_ID = models.ForeignKey(UserMatch, on_delete=models.CASCADE)
    IS_PAID = models.BooleanField(default=False)

    def __str__(self):
        return f"UserMatch: {self.USER_MATCH_ID} - Paid: {self.IS_PAID}"


class Payment(models.Model):
    PAYMENT_AMOUNT = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_DATE = models.DateTimeField(default=timezone.now)
    WALLET_ID = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    SUBSCRIPTION_ID = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    TEAM_REGISTRATION_ID = models.ForeignKey(TeamRegistrationFee, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Amount: {self.PAYMENT_AMOUNT} - Date: {self.PAYMENT_DATE}"


class Transaction(models.Model):
    TRANSACTION_DATE = models.DateTimeField(default=timezone.now)
    TRANSACTION_AMOUNT = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_ID = models.ForeignKey(Payment, on_delete=models.CASCADE)
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction Date: {self.TRANSACTION_DATE} - Amount: {self.TRANSACTION_AMOUNT} - User: {self.USER_ID.username}"
    
class JoinRequest(models.Model):
    PLAYER = models.ForeignKey(User, on_delete=models.CASCADE)
    TEAM = models.ForeignKey(Team, on_delete=models.CASCADE)
    STATUS = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    REQUESTED_AT = models.DateTimeField(auto_now_add=True)
    APPROVED_AT = models.DateTimeField(null=True, blank=True)
    REJECTED_AT = models.DateTimeField(null=True, blank=True)

    def approve(self):
        self.STATUS = 'approved'
        self.APPROVED_AT = timezone.now()
        self.save()

    def reject(self):
        self.STATUS = 'rejected'
        self.REJECTED_AT = timezone.now()
        self.save()

