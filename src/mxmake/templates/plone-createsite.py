from AccessControl.SecurityManagement import newSecurityManager
from plone.distribution.api.site import create
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Testing.makerequest import makerequest

import os
import transaction


TRUTHY = frozenset(("t", "true", "y", "yes", "on", "1"))


def asbool(value: str|bool|None) -> bool:
    """Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return value.strip().lower() in TRUTHY


DELETE_EXISTING = asbool(os.getenv("DELETE_EXISTING"))


app = makerequest(globals()["app"])
admin = app.acl_users.getUserById("admin")
newSecurityManager(None, admin.__of__(app.acl_users))

config = {
{% for key, value in site.items() %}
{% if key == "extension_ids" %}
{% for extension_id in value %}
    "extension_ids": [
        "{{ extension_id }}",
    ],
{% endfor %}
{% else %}
    "{{ key }}": "{{ value }}",
{% endif %}
{% endfor %}
    "profile_id": _DEFAULT_PROFILE,
}

if config["site_id"] in app.objectIds() and DELETE_EXISTING:
    app.manage_delObjects([config["site_id"]])
    transaction.commit()
    app._p_jar.sync()

if config["site_id"] not in app.objectIds():
    site = create(app, "{{ distribution }}", config)
    transaction.commit()
    app._p_jar.sync()
