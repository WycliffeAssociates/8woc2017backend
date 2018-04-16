from django.contrib.auth.hashers import make_password


def user_created(strategy, details, user=None, *args, **kwargs):
    if user:
        password = make_password("P@ssw0rd")

        user.is_social = True
        user.password = password
        user.save()
