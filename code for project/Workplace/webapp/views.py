# should use proper methods for request for security
# <a> GET
# <form> GET or POST
#in forms "get" method does embed all the name and values pair of "input" in the qyery params



from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .forms import *
from .models import *
import json
from django.core.paginator import Paginator

# Freelancer functionalities
@login_required
def chat(request, chat_id):
    try:
        chat=Chat.objects.get(id=chat_id)
    except:
        return HttpResponseForbidden("FORBIDDEN")
    
    if request.htmx:
        body=request.POST.get("body")
        message=Message.objects.create(chat=chat,author=request.user,body=body)
        content={"message":message}
        return render(request, "chat/message.html", content)
    
    try:
        messages=Message.objects.filter(chat=chat)
    except:
        messages=None
    content={"messages":messages,
             "chat_id":chat.id}
    return render(request, "chat/main.html", content)

@login_required
def create_chat(request,user_id):
    try:
        freelancer_id=request.GET.get("freelancer_id")
        freelancer=get_object_or_404(Custom_user,id=freelancer_id)
        client=get_object_or_404(Custom_user,id=user_id)
        if Chat.objects.filter(freelancer=freelancer,client=client).exists():
            chat=Chat.objects.get(freelancer=freelancer,client=client)
        else:
            chat=Chat.objects.create(freelancer=freelancer,client=client)
        
        return redirect(reverse("chat",kwargs={"chat_id":chat.id}))
    except:
        HttpResponseForbidden("FORBIDDEN")
    return HttpResponse("Failed", status=200)

@login_required
def wallet(request):
    if request.user.typee == "freelancer":
        wallet = Wallet.objects.get(user=request.user)
        content = {"wallet": wallet}
        return render(request, "wallet.html", content)
    else:
        return HttpResponseForbidden("You are not freelancer")

@login_required
@csrf_exempt
def withdraw(request):
    if request.user.typee == "freelancer":
        if request.method == "POST":
            amount = Decimal(request.POST.get("withdraw_amount"))
            desc = request.POST.get("desc")
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()
                Withdrwal(wallet=wallet, amount=amount, description=desc).save()
                return HttpResponse("Success", status=200)
            else:
                return HttpResponse("Failed", status=400)
    else:
        return HttpResponseForbidden("You are not freelancer")


@login_required
def project_progress(request, contract_id):
    if request.user.typee == "freelancer":
        contract = get_object_or_404(Contract, pk=contract_id, freelancer=request.user)
        try:
            print("hello in try")
            submission = Submission.objects.get(contract=contract)
            content = {
                "contract": contract,
                "flag": True,
                "payment": submission.is_approved,
            }
            return render(request, "project_progress.html", content)
        except:
            print("hello in except")
            if request.method == "POST":
                file = request.FILES.get("file")
                update = request.POST.get("progress")
                completed = "completed" in request.POST
                if completed is True:
                    submission = Submission(contract=contract, submission_file=file)
                    submission.save()
                    contract.completed = True
                    contract.save()
                    ProgressUpdate(contract=contract, update_text=update).save()
                    return redirect(
                        reverse("project_progress", kwargs={"contract_id": contract_id})
                    )

                else:
                    ProgressUpdate(contract=contract, update_text=update).save()
            updates = ProgressUpdate.objects.filter(contract=contract).order_by(
                "created_at"
            )

            content = {
                "contract": contract,
                "updates": updates,
                "flag": False,
                "payment": False,
            }
            return render(request, "project_progress.html", content)
    else:
        return HttpResponseForbidden("You are not freelancer")


@login_required
def approve_contract(request):
    if request.user.typee == "freelancer":
        if request.method == "POST":
            contract_id = request.POST.get("contract_id")
            contract = get_object_or_404(
                Contract, pk=contract_id, freelancer=request.user
            )
            if not contract.is_signed_by_freelancer:
                contract.is_signed_by_freelancer = True
                contract.save()
                return HttpResponse("Success", status=200)
            else:
                return HttpResponse("Already approved", status=200)
        return HttpResponse("Failed", status=400)
    else:
        return HttpResponseForbidden("You are not freelancer")


@login_required
def myprojects(request):
    if request.user.typee == "freelancer":
        all_contracts = Contract.objects.filter(freelancer=request.user)
        unsingned_contracts = all_contracts.filter(is_signed_by_freelancer=False)
        projects = all_contracts.filter(is_signed_by_freelancer=True)
        ongoing_projects = projects.filter(completed=False)
        completed_projects = projects.filter(completed=True)
        pending_feedback = completed_projects.filter(feedback_freelancer=False)
        completed_projects = completed_projects.filter(feedback_freelancer=True)
        content = {"contracts": unsingned_contracts, "projects": ongoing_projects,"pending_feedback":pending_feedback,"completed_projects":completed_projects}
        return render(request, "myprojects.html", content)
    else:
        return HttpResponseForbidden("You are not freelancer")



@login_required
def addbid(request):
    if request.user.typee == "freelancer":
        if request.method == "POST":
            postId = request.POST.get("post_id")
            amount = request.POST.get("amount")
            post = Post.objects.get(pk=postId)
            try:
                bid = Bid.objects.get(post_id=postId, freelancer=request.user)
            except Bid.DoesNotExist:
                bid = None
            print(bid)
            if bid is None:
                temp = Bid(freelancer=request.user, post_id=post, amount=amount).save()
                print(temp)
                return HttpResponse("Success", status=200)
        return HttpResponse("Failed", status=400)
    else:
        return HttpResponseForbidden("You are not freelancer")


@login_required
def e_home(request):
    if request.user.typee == "freelancer":
        try:
            bidded_posts = Bid.objects.filter(freelancer=request.user).values_list(
                "post_id", flat=True
            )
        except:
            bidded_posts = None
        tags = request.GET.get("search")
        if tags:
            tags = tags.split(" ")
            posts = Post.objects.all()
            for tag in tags:
                stripped_tag = tag.strip()
                posts = posts.filter(tags__string=stripped_tag).distinct()
            posts = posts.order_by("-created_at")
        else:
            posts = Post.objects.all().order_by("-created_at")
        if bidded_posts:
            posts = posts.exclude(pk__in=bidded_posts)
        try:
            contracts = Contract.objects.filter(
                is_signed_by_freelancer=True, is_signed_by_client=True
            )
        except:
            contracts = None
        if contracts:
            posts = posts.exclude(pk__in=[contract.post.id for contract in contracts])
        content = {"posts": posts}
        return render(request, "e_home.html", content)
    else:
        return HttpResponseForbidden("You are not freelancer")


@login_required
def withdrawl_history(request):
    if request.user.typee == "freelancer":
        wallt = get_object_or_404(Wallet, user=request.user)
        winthdraws = Withdrwal.objects.filter(wallet=wallt)
        return render(request, "withdrawl_history.html", {"winthdraws": winthdraws})
    else:
        return HttpResponseForbidden("You are not freelancer")


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.typee == "freelancer":
        return redirect("e_home")
    posts = Post.objects.all().order_by("-created_at")
    print(posts)
    content = {"posts": posts}
    return render(request, "home.html", content)


@login_required
def addfeedback(request):
    if request.user.typee == "freelancer":
        if request.method == "POST":
            contract_id = request.POST.get("contract_id")
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")
            try:
                contract = Contract.objects.get(pk=contract_id, freelancer=request.user)
            except:
                return HttpResponseForbidden("Contract not found")
            giver = request.user
            receiver = contract.client
            try:
                feedback = Feedback.objects.get(contract=contract, giver=giver)
            except:
                feedback = None
            if feedback is None:
                Feedback.objects.create(
                    contract=contract,
                    giver=giver,
                    receiver=receiver,
                    rating=rating,
                    comment=comment,
                )
                contract.feedback_freelancer = True
                contract.save()
                return HttpResponse("Success", status=200)
            else:
                return HttpResponseForbidden("You already gave feedback")
        return HttpResponseForbidden("You are not freelancer")
    else:
        return HttpResponseForbidden("You are not freelancer")


##################################################
# Client functionalities


@login_required
def view_post(request):
    if request.user.typee == "client":
        posts = Post.objects.filter(user=request.user)
        content = {"posts": posts}
        return render(request, "view_post.html", content)
    else:
        return HttpResponseForbidden("you are not client")


@login_required
def create_post(request):
    if request.user.typee == "client":
        if request.method == "POST":
            form = form_post(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                # because many to many relationships are stored in seperate table
                form.save_m2m()

                return redirect("home")
            else:
                error_data = json.dumps(form.errors)
                return HttpResponseForbidden(
                    error_data, content_type="application/json"
                )
        else:
            form = form_post()
            content = {"form": form}
            return render(request, "create_post.html", content)

    else:
        return HttpResponseForbidden("you are not client")


@login_required
def update_post(request, post_id):
    if request.user.typee == "client":
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        if request.method == "POST":
            form = form_post(request.POST, request.FILES, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()

                # because many to many relationships are stored in seperate table
                form.save_m2m()

                return redirect("home")
            else:
                error_data = json.dumps(form.errors)
                return HttpResponseForbidden(
                    error_data, content_type="application/json"
                )
        else:

            form = form_post(instance=post)
            content = {"form": form}
            return render(request, "create_post.html", content)

    else:
        return HttpResponseForbidden("you are not client")


@login_required
def delete_post(request, post_id):
    if request.user.typee == "client":
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        post.delete()
        return redirect("home")
    else:
        return HttpResponseForbidden("you are not client")


@login_required
def post_details(request, post_id):
    if request.user.typee == "client":
        try:
            post = Post.objects.get(pk=post_id, user=request.user)
            content = {"post": post}
            return render(request, "post_details.html", content)
        except Exception as e:
            exception = json.dumps(str(e))
            return HttpResponseForbidden(exception, content_type="application/json")
    else:
        return HttpResponseForbidden("you are not client")


@login_required
def view_post_bidders(request, post_id):
    if request.user.typee == "client":
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        bids = post.bids.all()
        
        return render(request, "view_post_bidders.html", {"bids": bids})
    else:
        return HttpResponseForbidden("You are not a client")


@csrf_exempt
@login_required
def create_contract(request, bid_id):
    if request.user.typee == "client":
        bid = get_object_or_404(Bid, pk=bid_id)
        if bid.post_id.user == request.user:
            check_contract = Contract.objects.filter(post=bid.post_id)
            if not check_contract:
                bid.status = True
                bid.save()
                if request.method == "POST":
                    contractt = Contract(
                        freelancer=bid.freelancer,
                        post=bid.post_id,
                        client=request.user,
                        amount=bid.amount,
                        details=request.POST.get("details"),
                        is_signed_by_client=True,
                    )
                    contractt.save()
                    progress = ProgressUpdate(contract=contractt)
                    progress.save()
                    return redirect("view_active_contracts")
                else:
                    return render(request, "create_contract.html")
            else:
                return HttpResponse("Contract already present")
        else:
            return HttpResponse("You don't own this post")
    else:
        return HttpResponseForbidden("You are not a client")


@login_required
def view_active_contracts(request):
    if request.user.typee == "client":
        category = request.GET.get("category", "all")  # Default to 'all'

        if category == "completed":
            contracts = Contract.objects.filter(completed=True, client=request.user)
        elif category == "pending_signature":
            contracts = Contract.objects.filter(
                is_signed_by_freelancer=False, client=request.user
            )
        elif category == "pending_feedback":
            contracts = Contract.objects.filter(
                completed=True, feedback_freelancer=False, client=request.user
            )
        else:  # 'all' or any other value
            contracts = Contract.objects.filter(client=request.user)


        paginator = Paginator(contracts, 3)  # Show 10 contracts per page
        page_number = request.GET.get('page')  # Get the current page number from the URL
        page_obj = paginator.get_page(page_number)
        
        active_contracts = []

        for contrct in page_obj:
            progress = ProgressUpdate.objects.filter(contract=contrct)
            try:
                submission = Submission.objects.get(contract=contrct)
            except:
                submission = None
            active_contracts.append(
                {"contract": contrct, "progress": progress, "submission": submission}
            )

        return render(
            request,
            "view_contracts.html",
            {"active_contracts": active_contracts,"page_obj": page_obj,},
        )
    else:
        return HttpResponseForbidden("You are not a client")


@login_required
def approve_work(request, contract_id):
    return redirect(reverse("pay_contract_amount", kwargs={"contract_id": contract_id}))


@csrf_exempt
@login_required
# also check submission in it
# can;t create a nodel object withour csrf verification
def pay_contract_amount(request, contract_id):
    if request.user.typee == "client":
        contrct = get_object_or_404(Contract, pk=contract_id, client=request.user)
        try:
            submission = Submission.objects.get(contract=contrct)
            bid=Bid.objects.get(post_id=contrct.post)
            if not submission.is_approved:
                if request.method == "POST":
                    amnt = Decimal(bid.amount)
                    freelancer = contrct.freelancer
                    payment = Payment(contract=contrct, amount=amnt)
                    wallet = get_object_or_404(Wallet, user=freelancer)
                    wallet.balance = wallet.balance + amnt
                    submission.is_approved = True
                    payment.save()
                    wallet.save()
                    submission.save()
                    return redirect("view_active_contracts")
                else:
                    return render(
                        request, "pay_contract_amount.html", {"submission": submission}
                    )
            else:
                return HttpResponse("Can't do it as work already approved")
        except:
            return HttpResponse("Can't do it as no submission present")
    else:
        return HttpResponseForbidden("You are not a client")


@login_required
def payment_history(request):
    if request.user.typee == "client":
        client = request.user
        contracts = client.contracts_as_client.all()
        payments = []
        for contract in contracts:
            try:
                payment = Payment.objects.get(contract=contract)
                payments.append(payment)
            except:
                pass

        return render(request, "payment_history.html", {"payments": payments})

    else:
        return HttpResponseForbidden("You are not a client")


@login_required
def bids_to_accept(request):
    if request.user.typee == "client":
        client = request.user
        posts = Post.objects.filter(user=client)
        bids = []
        for post in posts:
            bid = Bid.objects.filter(post_id=post, status=True)
            if not bid:
                bid = Bid.objects.filter(post_id=post)
                bids.extend(bid)

        return render(request, "bids_to_accept.html", {"bids": bids})

    else:
        return HttpResponseForbidden("You are not a client")


@login_required
def client_feedback(request):
    # Check if the user is a client
    if request.user.typee != "client":
        return HttpResponseForbidden("You are not authorized to perform this action.")

    if request.method == "POST":
        # Extract data from POST request
        contract_id = request.POST.get("contract_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        print(contract_id, rating, comment)
        contract = get_object_or_404(Contract, pk=contract_id, client=request.user)

        # Ensure feedback has not already been given
        feedback_exists = Feedback.objects.filter(
            contract=contract, giver=request.user
        ).exists()
        if feedback_exists:
            return JsonResponse(
                {"error": "You have already provided feedback for this contract."},
                status=403,
            )

        # Create feedback
        Feedback.objects.create(
            contract=contract,
            giver=request.user,
            receiver=contract.freelancer,
            rating=rating,
            comment=comment,
        )

        # Update contract status
        contract.feedback_client = True
        contract.save()

        return JsonResponse({"message": "Feedback submitted successfully."}, status=200)

    # Handle non-POST requests
    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def search_user(request):
    if request.user.typee != "client":
        return HttpResponseForbidden("You are not authorized to perform this action.")

    if request.method == "GET":
        query = request.GET.get("username", "").strip()

        if not query:
            return render(request,"search_user.html",{"users":None})

        # Filter freelancers whose usernames contain the query
        freelancers = Custom_user.objects.filter(username=query)

        # Convert QuerySet to list
        # results = list(freelancers)
        
        
        return render(request,"search_user.html",{"users":freelancers})

    # Invalid method handling
    return JsonResponse({"error": "Invalid request method."}, status=405)


#######################################################################
# admin functionalities


@login_required
def adminn(request):
    if request.user.typee == "admin":
        users = Custom_user.objects.exclude(typee="admin")
        return render(request, "admin.html", {"users": users})
    else:
        return HttpResponseForbidden("you are not admin")


@login_required
def verify_account(request, user_pk):
    if request.user.typee == "admin":
        userr = get_object_or_404(Custom_user, pk=user_pk)
        if userr.status == False:
            if request.method == "POST":

                form = verify_account_form(request.POST)
                if form.is_valid():
                    uni = form.cleaned_data["university_name"]
                    roll = form.cleaned_data["roll_no"].strip().lower()
                    uni_user = Custom_user.objects.filter(
                        university_name=uni, roll_no=roll
                    )

                    if not uni_user:
                        userr.status = True
                        userr.university_name = uni
                        userr.roll_no = roll
                        userr.save()
                        amount = Decimal(10000)
                        Wallet.objects.create(user=userr, balance=amount)
                        return redirect("adminn")
                    elif uni_user:
                        return HttpResponseForbidden("user already exists")
                else:
                    # Convert form.errors dictionary to JSON and return it in HttpResponseForbidden
                    error_data = json.dumps(
                        form.errors
                    )  # Convert the form errors dictionary to a JSON string
                    return HttpResponseForbidden(
                        error_data, content_type="application/json"
                    )
            elif request.method != "POST":
                form = verify_account_form()
                return render(request, "verify_account.html", {"form": form})

        elif userr.status == True:
            return redirect("adminn")

    else:
        return HttpResponseForbidden("you are not admin")


@login_required
def delete_account(request, user_pk):
    if request.user.typee == "admin":
        userr = get_object_or_404(Custom_user, pk=user_pk)
        userr.delete()
        return redirect("adminn")
    else:
        return HttpResponseForbidden("you are not admin")


@login_required
def tags(request):
    if request.user.typee == "admin":
        tags = Tags.objects.all()
        form = tag_creation()
        content = {"form": form, "tags": tags}
        return render(request, "tags.html", content)

    else:
        return HttpResponseForbidden("you are not admin")


@login_required
def create_tag(request):
    if request.user.typee == "admin":
        if request.method == "POST":
            form = tag_creation(request.POST)
            if form.is_valid():
                tag = form.save(commit=False)
                tag.save()
                return redirect("tags")
            else:
                error_data = json.dumps(form.errors)
                return HttpResponseForbidden(
                    error_data, content_type="application/json"
                )
        else:
            return HttpResponseForbidden("forbidden request method")

    else:
        return HttpResponseForbidden("you are not admin")


@login_required
def delete_tag(request, tag_id):
    if request.user.typee == "admin":
        try:
            tag = Tags.objects.get(pk=tag_id)
            tag.delete()
            return redirect("tags")
        except:
            return HttpResponseForbidden("tag doesnot found")

    else:
        return HttpResponseForbidden("you are not admin")


######################################################
# Registration


def user_register(request):
    if request.method == "POST":
        form = form_user(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect("home")
        else:

            error_data = json.dumps(form.errors)
            return HttpResponseForbidden(error_data, content_type="application/json")

    else:
        logout(request)
        form = form_user()
        return render(request, "register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.typee == "admin":
                login(request, user)
                return redirect("adminn")
            else:
                if user.status == True:
                    login(request, user)
                    return redirect("home")
                else:
                    return HttpResponseForbidden("you are not verified yet")
        else:
            # Convert form.errors dictionary to JSON and return it in HttpResponseForbidden
            error_data = json.dumps(
                form.errors
            )  # Convert the form errors dictionary to a JSON string
            return HttpResponseForbidden(error_data, content_type="application/json")

    else:
        form = AuthenticationForm()
        return render(request, "login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("home")  # Redirect to login page after logout


@login_required
def profile(request,user_pk):
    if user_pk:
        user=get_object_or_404(Custom_user,pk=user_pk)
        return render(request, "profile.html",{"userr":user})
        
