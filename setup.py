from setuptools import find_packages, setup

LONG_DESCRIPTION = """
.. image:: http://pinaxproject.com/pinax-design/patches/pinax-notifications.svg
    :target: https://pypi.python.org/pypi/pinax-notifications/

===================
Pinax Notifications
===================

.. image:: https://img.shields.io/pypi/v/pinax-notifications.svg
    :target: https://pypi.python.org/pypi/pinax-notifications/
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://pypi.python.org/pypi/pinax-notifications/

.. image:: https://img.shields.io/circleci/project/github/pinax/pinax-notifications.svg
    :target: https://circleci.com/gh/pinax/pinax-notifications
.. image:: https://img.shields.io/codecov/c/github/pinax/pinax-notifications.svg
    :target: https://codecov.io/gh/pinax/pinax-notifications
.. image:: https://img.shields.io/github/contributors/pinax/pinax-notifications.svg
    :target: https://github.com/pinax/pinax-notifications/graphs/contributors
.. image:: https://img.shields.io/github/issues-pr/pinax/pinax-notifications.svg
    :target: https://github.com/pinax/pinax-notifications/pulls
.. image:: https://img.shields.io/github/issues-pr-closed/pinax/pinax-notifications.svg
    :target: https://github.com/pinax/pinax-notifications/pulls?q=is%3Apr+is%3Aclosed

.. image:: http://slack.pinaxproject.com/badge.svg
    :target: http://slack.pinaxproject.com/

``pinax-notifications`` is a user notification management app for the Django web framework.
 
``pinax-notifications`` notifies users when certain events have occurred and allows
configurable options as to how those notifications are to be received.

Features
--------

* Submission of notification messages by other apps
* Notification messages on signing in
* Notification messages via email (configurable by user)
* Ability to supply your own backend notification channels

Supported Django and Python Versions
------------------------------------

* Django 1.8, 1.10, 1.11, and 2.0
* Python 2.7, 3.4, 3.5, and 3.6
"""

setup(
    author="Pinax Team",
    author_email="team@pinaxprojects.com",
    description="User notification management for the Django web framework",
    name="pinax-notifications",
    long_description=LONG_DESCRIPTION,
    version="4.1.0",
    url="http://github.com/pinax/pinax-notifications/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "notifications": []
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "django>=1.8",
        "django-appconf>=1.0.1",
    ],
    tests_require=[
    ],
    test_suite="runtests.runtests",
    zip_safe=False
)
