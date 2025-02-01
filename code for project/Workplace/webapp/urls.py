from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/<int:user_pk>/", views.profile, name="profile"),
    path("chat/<chat_id>", views.chat, name="chat"),
    path("chat/create/<user_id>", views.create_chat, name="create_chat"),
    ############################################################
    #  freelancers
    path("e_home", views.e_home, name="e_home"),
    path("addbid", views.addbid, name="addbid"),
    path("myprojects", views.myprojects, name="myprojects"),
    path("wallet", views.wallet, name="wallet"),
    path("withdraw", views.withdraw, name="withdraw"),
    path("approve_contract", views.approve_contract, name="approve_contract"),
    path(
        "project_progress/<int:contract_id>",
        views.project_progress,
        name="project_progress",
    ),
    path("withdrawl_history", views.withdrawl_history, name="withdrawl_history"),
    path("client_feedback", views.client_feedback, name="client_feedback"),
    ############################################################
    # clients
    path("create", views.create_post, name="create_post"),
    path("update/<int:post_id>", views.update_post, name="update_post"),
    path("delete/<int:post_id>", views.delete_post, name="delete_post"),
    path("view_post", views.view_post, name="view_post"),
    path("post_details/<int:post_id>", views.post_details, name="post_details"),
    path(
        "view_post_bidders/<int:post_id>",
        views.view_post_bidders,
        name="view_post_bidders",
    ),
    path(
        "create_contract/<int:bid_id>",
        views.create_contract,
        name="create_contract",
    ),
    path(
        "view_active_contracts",
        views.view_active_contracts,
        name="view_active_contracts",
    ),
    path("approve_work/<int:contract_id>/", views.approve_work, name="approve_work"),
    path(
        "pay_contract_amount/<int:contract_id>",
        views.pay_contract_amount,
        name="pay_contract_amount",
    ),
    path("payment_history", views.payment_history, name="payment_history"),
    path("bids_to_accept", views.bids_to_accept, name="bids_to_accept"),
    path("addfeedback", views.addfeedback, name="addfeedback"),
    ############################################################
    # admin
    path("adminn", views.adminn, name="adminn"),
    path("verify_account/<int:user_pk>", views.verify_account, name="verify_account"),
    path("delete_account/<int:user_pk>", views.delete_account, name="delete_account"),
    path("delete_tag/<int:tag_id>", views.delete_tag, name="delete_tag"),
    path("tags", views.tags, name="tags"),
    path("create_tag", views.create_tag, name="create_tag"),
    ############################################################
    # registration
    path("register/", views.user_register, name="register"),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),
    path("search_user", views.search_user, name="search_user"),
]
