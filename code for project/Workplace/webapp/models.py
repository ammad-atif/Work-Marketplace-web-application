from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date

#users should be differnet modals because while registration frontend can be manipulated and a user can become the admin if he manipulates the frontend but a type of "admin" from the frontend, the form validation will fail because "admin" is not part of the predefined TYPE_CHOICES list. The ChoiceField will only accept values from the options you specified in the TYPE_CHOICES list, which are "client" and "freelancer."


# Create your models here.


class Custom_user(AbstractUser):
    TYPE_CHOICES = [
        ("admin", "Administrator"),
        ("client", "Client"),
        ("freelancer", "Freelancer"),
    ]
    typee = models.CharField(
        max_length=50, null=False, blank=False, choices=TYPE_CHOICES, default=""
    )

    status = models.BooleanField(null=False, default=False)

    img = models.ImageField(upload_to="images/", null=False, blank=True, default="")

    UNI_CHOICES = [
        ("fast", "FAST"),
        ("lums", "LUMS"),
        ("punjab", "PUNJAB UNIVERSITY"),
    ]
    university_name = models.CharField(
        max_length=50, null=False, blank=False, choices=UNI_CHOICES, default=""
    )
    roll_no = models.CharField(max_length=50, null=False, blank=False, default="")

    email = models.EmailField(
        unique=True, blank=False, null=False
    )  # Ensure email is unique


class Tags(models.Model):
    string = models.TextField(max_length=50, default="")

    def __str__(self):
        return f"{self.string}"

class Chat(models.Model):
    freelancer = models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name="freelancer")
    client = models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name="client")
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    body = models.TextField(max_length=1000, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Message from {self.author} for {self.chat.id}"

class Post(models.Model):
    user = models.ForeignKey(
        Custom_user, on_delete=models.CASCADE, blank=False, null=False
    )
    title = models.TextField(max_length=50, blank=False, null=False)
    text = models.TextField(max_length=1000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    tags = models.ManyToManyField(Tags, related_name="posts", blank=True)
    pay = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Wallet(models.Model):
    user = models.OneToOneField(
        Custom_user, on_delete=models.CASCADE, blank=False, null=False
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False, default=0
    )

    def __str__(self):
        return f"Wallet for {self.user.username} : Rs. {self.balance}"


class Withdrwal(models.Model):
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, blank=False, null=False
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    description = models.TextField(max_length=1000, blank=False, null=False, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description.capitalize()} of {self.amount} for Wallet {self.wallet.id}"


class Bid(models.Model):
    freelancer = models.ForeignKey(Custom_user, on_delete=models.CASCADE, null=False)
    post_id = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=False, related_name="bids"
    )
    status = models.BooleanField(default=False)
    amount = models.FloatField(null=False, blank=False, help_text="Enter amount to bid")
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        unique_together = ("freelancer_id", "post_id")


class Contract(models.Model):
    client = models.ForeignKey(
        Custom_user, on_delete=models.CASCADE, related_name="contracts_as_client"
    )
    freelancer = models.ForeignKey(
        Custom_user, on_delete=models.CASCADE, related_name="contracts_as_freelancer"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, null=False, blank=False
    )  # Contract may or may not link to a post
    created_at = models.DateTimeField(auto_now_add=True)

    details = models.TextField(max_length=1000, null=True, blank=True, default="")
    deadline = models.DateField(null=False, blank=False, default=date.today)
    is_signed_by_client = models.BooleanField(default=False)
    is_signed_by_freelancer = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    feedback_freelancer= models.BooleanField(default=False)
    feedback_client= models.BooleanField(default=False)
    # def clean(self):
    #     if self.client.typee != "client":
    #         raise ValidationError("The selected client does not have type 'client'.")
    #     if self.freelancer.typee != "freelancer":
    #         raise ValidationError(
    #             "The selected freelancer does not have type 'freelancer'."
    #         )

    # def save(self, *args, **kwargs):
    #     self.clean()  # Ensure validation is called before saving
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Contract between {self.client.username} and {self.freelancer.username}"


class ProgressUpdate(models.Model):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="progress_contract"
    )
    progress_percentage = models.PositiveIntegerField(
        default=0
    )  # Percentage from 0 to 100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    update_text = models.TextField(max_length=500, default="")

    def __str__(self):
        return f"Progress Update for Contract {self.contract.id} - {self.progress_percentage}%"


class Submission(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,related_name="submission_contract")
    submission_file = models.FileField(
        upload_to="submissions/", null=False, blank=False
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    #is_approved===is_payed()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Submission for Contract {self.contract.id} - Approved: {self.is_approved}"
        )


class Feedback(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    giver = models.ForeignKey(
        Custom_user, on_delete=models.CASCADE, related_name="given_feedbacks"
    )
    receiver = models.ForeignKey(
        Custom_user, on_delete=models.CASCADE, related_name="received_feedbacks"
    )
    rating = models.PositiveIntegerField(null=False, blank=False)  # Rating out of 5
    comment = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.giver.username} for {self.receiver.username}"


class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"payment of {self.amount} for Contract {self.contract.id}"


# class Chat(models.Model):
#     sender = models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField(max_length=1000, null=False, blank=False)
#     sent_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.username} to {self.receiver.username}"
