![](http://pinaxproject.com/pinax-design/patches/pinax-notifications.svg)

# Pinax Notifications

[![](https://img.shields.io/pypi/v/pinax-notifications.svg)](https://pypi.python.org/pypi/pinax-notifications/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/pinax-notifications/)

[![CircleCi](https://img.shields.io/circleci/project/github/pinax/pinax-notifications.svg)](https://circleci.com/gh/pinax/pinax-notifications)
[![Codecov](https://img.shields.io/codecov/c/github/pinax/pinax-notifications.svg)](https://codecov.io/gh/pinax/pinax-notifications)
![](https://img.shields.io/github/contributors/pinax/pinax-notifications.svg)
![](https://img.shields.io/github/issues-pr/pinax/pinax-notifications.svg)
![](https://img.shields.io/github/issues-pr-closed/pinax/pinax-notifications.svg)

[![](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)


`pinax-notifications` is a user notification management app for the Django web framework. 
Many sites need to notify users when certain events have occurred and to allow
configurable options as to how those notifications are to be received. `pinax-notifications` serves this need.

### Features

* Submission of notification messages by other apps
* Notification messages on signing in
* Notification messages via email (configurable by user)
* Ability to supply your own backend notification channels

### Supported Django and Python Versions

* Django 1.8, 1.10, 1.11, and 2.0
* Python 2.7, 3.4, 3.5, and 3.6


## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Settings](#settings)
* [Signals](#signals)
* [Scoping Notifications](#scoping-notifications)
* [Template Tags](#template-tags)
* [Change Log](#change-log)
* [Project History](#project-history)
* [About Pinax](#about-pinax)


## Installation

To install pinax-announcements:

    pip install pinax-announcements

Add `pinax.announcements` to your `INSTALLED_APPS` setting:

    INSTALLED_APPS = (
        ...
        "pinax.announcements",
        ...
    )

Optionally, if you want someone other than staff to manage announcements,
enable this authentication backend:

    AUTHENTICATION_BACKENDS = [
        ...
        "pinax.announcements.auth_backends.AnnouncementPermissionsBackend",
        ...
    ]

then enable permission `"announcements.can_manage"` for these managers.

Lastly add `pinax.announcements.urls` to your project urlpatterns:

    urlpatterns = [
        ...
        url(r"^announcements/", include("pinax.announcements.urls", namespace="pinax_announcements")),
        ...
    ]


## Usage

Integrating notification support into your app is a simple three-step process:

1. create your notice types
1. create your notice templates
1. send notifications


### Creating Notice Types

You need to call `NoticeType.create(label, display, description)` once to
create the notice types for your application in the database.
 
* `label` is the internal shortname that will be used for the type
* `display` is what the user sees as the name of the notification type
* `description` is a short description

For example:

    from pinax.notifications.models import NoticeType
    
    NoticeType.create(
        "friends_invite",
        "Invitation Received",
        "you have received an invitation"
    )

One way to create notice types is using a custom `AppConfig`. Here is an example:

    # myapp/signals/handlers.py
    from django.conf import settings
    from django.utils.translation import ugettext_noop as _
    
    def create_notice_types(sender, **kwargs): 
        if "pinax.notifications" in settings.INSTALLED_APPS:
            from pinax.notifications.models import NoticeType
       	    print "Creating notices for myapp" 
            NoticeType.create("friends_invite", _("Invitation Received"), _("you have received an invitation"))
            NoticeType.create("friends_accept", _("Acceptance Received"), _("an invitation you sent has been accepted"))
        else:
            print "Skipping creation of NoticeTypes as notification app not found"

Notice that the code is wrapped in a conditional clause so if
`pinax-notifications` is not installed, your app will proceed anyway.

Note that the display and description arguments are marked for translation by
using ugettext_noop. That will enable you to use Django's makemessages
management command and use `pinax-notifications` i18n capabilities.

    # myapp/apps.py
    from django.apps import AppConfig
    from django.db.models.signals import post_migrate

    from myapp.signals import handlers

    class MyAppConfig(AppConfig):
        name = 'myapp'
        verbose_name = 'My App'
    
        def ready(self):
            post_migrate.connect(handlers.create_notice_types, sender=self)

This will call the handler to create notices after the application is migrated.

    # myapp/__init__.py
    default_app_config = 'myapp.apps.MyAppConfig'

### Creating Templates

### `pinax/notifications/notice_settings.html`

This is a template that ships with `pinax-notifications` and provides an
interview for the user setting of notices that they want to receive. It is
rendered by the sole view in `pinax.notifications.views` with the context that
is a list of available `notice_types` as well as the `request.user`'s settings
for those notice types.

### Backends

Each backend will have it's own requirements in terms of template(s) it needs
as well as the context it provides in rendering them. It is possible that some
backends may not even use templates.

There are two templates that ship with `pinax-notifications` in support of the
single email backend that is included out of the box:

* ``short.txt`` renders to the email subject
* ``full.txt`` renders to the email body

In addition to the extra context that is supplied via the `send` call in your
site or app, these templates are rendered with the following context variables:

* `default_http_protocol` - `https` if `settings.PINAX_USE_SSL` is True, otherwise `http`
* `current_site` - `Site.objects.get_current()`
* `base_url` - the default http protocol combined with the current site domain
* `recipient` - the user who is getting the notice
* `sender` - the value supplied to the `sender` kwarg of the `send` method (often this is not set and will be `None`)
* `notice` - display value of the notice type

These two templates that ship with `pinax-notifications` and live at
`pinax/notifications/short.txt` and `pinax/notifications/full.txt` are pretty
vanilla and default. You will likely want to have per notice type
customizations.

In order to do this, each of these templates should be put in a directory on
the template path called `pinax/notifications/<notice_type_label>/<template_name>`.

If any of these are missing, a default would be used.

### Sending Notifications

There are two different ways of sending out notifications. We have support
for blocking and non-blocking methods of sending notifications. The most
simple way to send out a notification, for example::

    send([to_user], "friends_invite", {"from_user": from_user})

One thing to note is that `send` is a proxy around either `send_now` or
`queue`. They all have the same signature::

    send(users, label, extra_context)

The parameters are:

* `users` is an iterable of `User` objects to send the notification to.
* `label` is the label you used in the previous step to identify the notice type.
* `extra_content` is a dictionary to add custom context entries to the template
   used to render to notification. This is optional.


#### `send_now` vs. `queue` vs. `send`

Lets first break down what each does.

##### `send_now`

This is a blocking call that will check each user for elgibility of the
notice and actually peform the send.

##### `queue`

This is a non-blocking call that will queue the call to `send_now` to
be executed at a later time. To later execute the call you need to use
the `emit_notices` management command.


##### `send`

A proxy around `send_now` and `queue`. It gets its behavior from a global
setting named `PINAX_NOTIFICATIONS_QUEUE_ALL`. By default it is `False`. This
setting is meant to help control whether you want to queue any call to `send`.

`send` also accepts `now` and `queue` keyword arguments. By default each option
is set to `False` to honor the global setting which is `False`. This enables
you to override on a per call basis whether it should call `send_now` or
`queue`.


### Optional Notification Support

In case you want to use `pinax-notification` in your reusable app, you can wrap
the import of `pinax-notification` in a conditional clause that tests if it's
installed before sending a notice. As a result your app or project still
functions without notification.

For example:

    from django.conf import settings

    if "notification" in settings.INSTALLED_APPS:
        from pinax.notifications import models as notification
    else:
        notification = None

and then, later:

    if notification:
        notification.send([to_user], "friends_invite", {"from_user": from_user})


## Settings

The following allows you to specify the behavior of `pinax-notifications` in
your project. Please be aware of the native Django settings which can affect
the behavior of `pinax-notification`.


### PINAX_NOTIFICATIONS_BACKENDS

Formerly, this setting was `NOTIFICATION_BACKENDS`.

Defaults to:

    [
        ("email", "pinax.notifications.backends.email.EmailBackend"),
    ]


### PINAX_USE_SSL

_This is a proposed common setting across the Pinax ecosystem. It currently may
not be consistant across all apps._

Formerly, this setting was `DEFAULT_HTTP_PROTOCOL` and defaulted to `http`.

It now defaults to `False`.

This is used to specify the beginning of URLs in the default `email_body.txt`
file. A common use-case for overriding this default might be `https` for use on
more secure projects.


### PINAX_NOTIFICATIONS_LANGUAGE_MODEL

Formerly, this setting was `NOTIFICATION_LANGUAGE_MODULE`

There is not set default for this setting. It allows users to specify their own
notification language.

Example model in a `languages` app::

    from django.conf import settings

    class Language(models.Model):
    
        user = models.ForeignKey(User)
        language = models.CharField(max_length=10, choices=settings.LANGUAGES)


Setting this value in `settings.py`::

    PINAX_NOTIFICATIONS_LANGUAGE_MODEL = "languages.Language"


### DEFAULT_FROM_EMAIL

Defaults to `webmaster@localhost` and is a [standard Django setting](https://docs.djangoproject.com/en/1.7/ref/settings/#default-from-email).

Default e-mail address to use for various automated correspondence from
`pinax.notifications.backends.email`.


### LANGUAGES

Defaults to a tuple of all available languages and is a
[standard Django setting](https://docs.djangoproject.com/en/1.7/ref/settings/#languages).

The default for this is specifically used for things like the Django admin.
However, if you need to specify a subset of languages for your site's front end
you can use this setting to override the default. In which case this is the
definated pattern of usage::

    gettext = lambda s: s

    LANGUAGES = (
        ("en", gettext("English")),
        ("fr", gettext("French")),
    )


### PINAX_NOTIFICATIONS_QUEUE_ALL

Formerly, this setting was `NOTIFICATION_QUEUE_ALL`.

It defaults to `False`.

By default, calling `notification.send` will send the notification immediately,
however, if you set this setting to True, then the default behavior of the
`send` method will be to queue messages in the database for sending via the
`emit_notices` command.


### PINAX_NOTIFICATIONS_LOCK_WAIT_TIMEOUT

Formerly, this setting was `NOTIFICATION_LOCK_WAIT_TIMEOUT`.

It defaults to `-1`.

It defines how long to wait for the lock to become available. Default of -1
means to never wait for the lock to become available. This only applies when
using crontab setup to execute the `emit_notices` management command to send
queued messages rather than sending immediately.


## Signals

### pinax.announcements.signals.announcement_created

This signal is sent immediately after an announcement is created.
It provides a single `kwarg` of `announcement`, the created `Announcement` instance.
Sender is the newly created Announcement instance.

### pinax.announcements.signals.announcement_updated

This signal is sent immediately after an announcement is updated.
It provides a single `kwarg` of `announcement`, the updated `Announcement` instance.
Sender is the newly updated Announcement instance.

### pinax.announcements.signals.announcement_deleted

This signal is sent immediately after an announcement is deleted.
It provides a single `kwarg` of `announcement`, the deleted `Announcement` instance.
Sender is `None`.


## Scoping Notifications

Sometimes you have a site that has groups or teams. Perhaps you are using
[pinax-teams](https://github.com/pinax/pinax-teams/). If this is the case you
likely want users who might be members of multiple teams to be able to set
their notification preferences on a per team or group basis.

You will need to to simply override `NoticeSettingsView` to provide your own
scoping object.

### Override NoticeSettingsView

I think it's best if we just demonstrate via code:

    # views.py
    from pinax.notifications.views import NoticeSettingsView
    
    
    class TeamNoticeSettingsView(NoticeSettingsView):
        
        @property
        def scoping(self):
            return self.request.team


Then override the url:

    # urls.py
    from django.conf.urls import patterns, url
    
    from .views import TeamNoticeSettingsView
    
    
    urlpatterns = patterns(
        "",
        ...
        url(r"^notifications/settings/$", TeamNoticeSettingsView.as_view(), name="notification_notice_settings"),
    )


## Template Tags

### announcements

Filters announcements by `publish_start` and `publish_end` date range, including
all with no `publish_end` value.
Returns announcements matching `site_wide == True` and `members_only == False`,
and which are not dismissed.

    {% announcements as announcement_list %}
    {% for announcement in announcement_list %}
        <div>
            {{ announcement.title }}<br />
            {{ announcement.content }}
        </div>
    {% endfor %}


## Change Log

_*BI*_ = backward incompatible change

### 4.1.0

* Add Django 2.0 compatibility testing
* Drop Django 1.9 and Python 3.3 support
* Move documentation into README
* Convert CI and coverage to CircleCi and CodeCov
* Add PyPi-compatible long description

### 4.0
* _*BI*_: To support changes to `render_to_string` in Django 1.10 and above,
your notice `full.txt` and `short.txt` plain text templates must now be autoescaped explicitly using the
`{% autoescape %}` tag.
([#68](https://github.com/pinax/pinax-notifications/issues/68#issuecomment-258383323)) 


### 3.0.1
* initial support for Django 1.10


### 3.0
* fix compatability with Django migrations


### 2.1.0
* add Django migrations


### 2.0

* renamed app as pinax-notifications
* added the ability to override NoticeSetting model
* added documentation on scoping notifications


### 1.1.1

* fixed a deprecation warning


### 1.1

* added Russian locale
* added travis integration for tests/lints
* added created_notice_type wrapper
* cleaned up some small bugs identified by pylint


### 1.0

* removed unused `message.py` module
* removed `captureas` templatetag
* added `notice_settings.html` template
* other minor fixes and tweaks, mostly to code style

### 0.3

* pluggable backends


### 0.2.0

* BI: renamed Notice.user to Notice.recipient
* BI: renamed {{ user }} context variable in notification templates to
  {{ recipient }}
* BI: added nullable Notice.sender and modified send_now and queue to take
  an optional sender
* added received and sent methods taking a User instance to Notice.objects
* New default behavior: single notice view now marks unseen notices as seen
* no longer optionally depend on mailer; use django.core.mail.send_mail and
  we now encourge use of Django 1.2+ for mailer support
* notifications are not sent to inactive users
* users which do not exist when sending notification are now ignored
* BI: split settings part of notices view to its own view notice_settings


### 0.1.5

* added support for DEFAULT_HTTP_PROTOCOL allowing https absolute URLs


## Project History

This app was originally named `django-notification` but was renamed to
bring a common package name like `notification` under the `pinax` namespace
to avoid conflicts with other like named packages.

In addition, we wanted to take the opportunity to rename it to the plural
form, `notifications` to be in line with the convention we've adopted
across the ecosystem.


## About Pinax

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable Django apps, themes, and starter project templates. This collection can be found at http://pinaxproject.com.

The Pinax documentation is available at http://pinaxproject.com/pinax/. If you would like to help us improve our documentation or write more documentation, please join our Pinax Project Slack team and let us know!

For updates and news regarding the Pinax Project, please follow us on Twitter at @pinaxproject and check out our blog http://blog.pinaxproject.com.
