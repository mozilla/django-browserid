from django.dispatch import Signal


"""
Signal triggered when the BrowserID authentication backend creates a new
user.

Sender is the function that created the user, user is the new user instance.
"""
user_created = Signal(providing_args=['user'])