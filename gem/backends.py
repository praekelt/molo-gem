"""
This package contains customisations specific to the Girl Effect project.
The technical background can be found here:
https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#additional-optional-configuration
"""
import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Group

USERNAME_FIELD = "username"
EMAIL_FIELD = "email"

LOGGER = logging.getLogger(__name__)


def _update_user_from_claims(user, claims):
    """
    Update the user profile with information from the claims.
    This function is called on registration (new user) as well as login events.
    This function provides the mapping from the OIDC claims fields to the
    internal user profile fields.
    In this example we use the role names as the names for Django
    Groups to which a user belongs.
    :param user: The user profile
    :param claims: The claims for the profile
    """
    LOGGER.debug("Updating user {} with claims: {}".format(user, claims))

    user.first_name = claims.get("given_name") or claims["nickname"]
    user.last_name = claims.get("family_name") or ""
    user.email = claims.get("email") or ""
    user.save()

    # Synchronise the roles that the user has.
    # The list of roles may contain more or less roles
    # than the previous time the user logged in.
    roles = set(claims.get("roles", []))
    groups = set(group.name for group in user.groups.all())

    # If the user has any role, we assume that it is a staff user
    # This is just to get logging in working on Core QA site
    if roles:
        user.is_staff = True
        user.save()

    groups_to_add = roles - groups
    groups_to_remove = groups - roles

    for group_name in groups_to_add:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            LOGGER.debug("Created new group: {}".format(group_name))
        user.groups.add(group)
    LOGGER.debug("Added groups to user {}: {}".format(user, groups_to_add))

    args = [
        Group.objects.get(name=group_name) for group_name in groups_to_remove]
    user.groups.remove(*args)
    LOGGER.debug(
        "Removed groups from user {}: {}".format(user, groups_to_remove))

    site_specific_data = claims.get("site")
    if site_specific_data:
        LOGGER.debug("Got site specific data: {}".format(site_specific_data))


class GirlEffectOIDCBackend(OIDCAuthenticationBackend):

    def filter_users_by_claims(self, claims):
        """
        The default behaviour is to look up users based on their email
        address. However, in the Girl Effect ecosystem the email is optional,
        so we prefer to use the UUID associated with the user profile (
        subject identifier)
        :return: A user identified by the claims, else None
        """
        uuid = claims["sub"]
        try:
            kwargs = {USERNAME_FIELD: uuid}
            user = self.UserModel.objects.get(**kwargs)
            # Update the user with the latest info
            return [user]
        except self.UserModel.DoesNotExist:
            LOGGER.debug("Lookup failed based on {}".format(kwargs))

        return self.UserModel.objects.none()

    def create_user(self, claims):
        """Return object for a newly created user account.
        The default OIDC client create_user() function expects an email address
        to be available. This is not the case for Girl Effect accounts, where
        the email field is optional.
        We use the user id (called the subscriber identity in OIDC) as the
        username, since it is always available and guaranteed to be unique.
        """
        username = claims["sub"]  # The sub field _must_ be in the claims.
        # We create the user based on the username.
        email = claims.get("email")  # Email is optional
        # We create the user based on the username and optional email fields.
        user = self.UserModel.objects.create_user(username, email)
        _update_user_from_claims(user, claims)
        return user

    def verify_claims(self, claims):
        """
        This function can be used to prevent authorisation of users based
        on claims information.
        """
        verified = super(GirlEffectOIDCBackend, self).verify_claims(claims)
        # Example of how to prevent users without a verified email from
        # logging in.
        # verified = verified and claims.get("email_verified")
        return verified
