def build_url(request, url):
    return request.build_absolute_uri(url)


def get_confirmation_url(request, user):
    return build_url(request, "/confirm/{}".format(user.confirmation_token))


def get_reset_password_url(request, user):
    return build_url(request, "/reset-password/{}".format(user.reset_password_token))
