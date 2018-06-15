# -*- coding: utf-8 -*-
# Copyright (c) 2016, Semilimes
# For license information, please see license.txt

import json
import urllib
import requests
from functools import wraps

import frappe

from .account import global_unsubscribe_and_commit


def api_url(api_endpoint):
    """
    Get SendGrid API URL for syncing webhooks.

    :param api_endpoint: SendGrid API endpoint, will be appended to API url
    """
    return urllib.basejoin('https://api.sendgrid.com/v3/', api_endpoint.lstrip("/"))


def auth_header(api_key):
    """
    Get SendGrid authorization header for API key.

    :param api_key: SendGrid API key to use for authorization
    """
    return {"Authorization": "Bearer {}".format(api_key)}


def handle_http_error(response):
    """
    Check HTTP response for errors and process them accordingly.

    :param response: HTTP response to check
    """
    if response.status_code != 200:
        # check if there is some info about error in json format
        if response.headers.get("content-type") == "application/json":
            error_json = response.json().get("errors")

            # log every error
            for error in error_json:
                frappe.errprint("SendGrid HTTP error {}: {}".format(
                    response.status_code, error.get("message")))
        else:
            # log status code at least
            frappe.errprint("SendGrid HTTP error {}: {}".format(
                response.status_code, response.text))
        return True
    return False


def handle_request_errors(request_method):
    """Decorator that handles errors and provides correct log messages."""
    @wraps(request_method)
    def safe_request_method(*args, **kwargs):
        try:
            return request_method(*args, **kwargs)
        except requests.ConnectionError:
            frappe.errprint("Failed to connect to SendGrid API")
        except Exception as e:
            frappe.errprint("SendGrid API Request Error: {}".format(e.message))
    return safe_request_method


@handle_request_errors
def webhook_exists(api_key, webhook_post_url):
    """
    Use SendGrid API to find out if webhook exists already.

    :param api_key: SendGrid API key, should be generated in SendGrid settings
    :param webhook_post_url: full url for SendGrid webhook with credentials

    Response JSON data example from
    https://sendgrid.com/docs/API_Reference/Web_API_v3/Webhooks/event.html

    {
        "enabled": true,
        "url": "url",
        "group_resubscribe": true,
        "delivered": true,
        "group_unsubscribe": true,
        "spam_report": true,
        "bounce": true,
        "deferred": true,
        "unsubscribe": true,
        "processed": true,
        "open": true,
        "click": true,
        "dropped": true
    }
    """
    r = requests.get(api_url("/user/webhooks/event/settings"),
                     headers=auth_header(api_key))

    if handle_http_error(r):
        return

    return _webhook_enabled(r.json(), webhook_post_url)


def _webhook_enabled(settings, webhook_post_url):
    if settings.get("enabled") is True and settings.get("url") == webhook_post_url:
        return True

    return False


@handle_request_errors
def add_webhook(api_key, webhook_post_url):
    """
    Use SendGrid API to setup events webhook for given url.

    :param api_key: SendGrid API key, should be generated in SendGrid settings
    :param webhook_post_url: url for SendGrid events webhook

    Note that SendGrid webhooks only support basic HTTP authentication so username
    and password should be generated and included in webhook url like this:
    http(s)://username:password@domain/foo.php

    More on SendGrid webhooks here:
    https://sendgrid.com/docs/API_Reference/Webhooks/event.html
    """
    webhook_settings = {"enabled": True,
                        "url": webhook_post_url,
                        "group_resubscribe": True,
                        "delivered": True,
                        "group_unsubscribe": True,
                        "spam_report": True,
                        "bounce": True,
                        "deferred": True,
                        "unsubscribe": True,
                        "processed": True,
                        "open": True,
                        "click": True,
                        "dropped": True,
                        }

    r = requests.patch(api_url("/user/webhooks/event/settings"),
                       data=json.dumps(webhook_settings),
                       headers=auth_header(api_key))

    if handle_http_error(r):
        return

    return _webhook_enabled(r.json(), webhook_post_url)


@handle_request_errors
def unsubscribe_emails(api_key, endpoint, batch_key="emails", remove_endpoint=None):
    """
    Receive list of emails from SendGrid and unsubscribe each email.

    :param api_key: SendGrid API key, should be generated in SendGrid settings
    :param endpoint: API endpoint to use in order to get list of emails
    :param batch_key: key to group emails and perform batch deletion with one request. If
                      not present - each deletion will become an individual request.
    :param remove_endpoint: API endpoint to use in order to remove email from list. If
                            not present - endpoint for retrieval will be used as removal
                            endpoint.
    """
    if not remove_endpoint:
        remove_endpoint = endpoint

    header = auth_header(api_key)
    r = requests.get(api_url(endpoint), headers=header)

    # process errors
    if handle_http_error(r):
        return

    emails = [item["email"] for item in r.json()]
    if not emails:
        return

    # unsubscribe and remove
    if batch_key:
        # perform batch request
        request_data = json.dumps({batch_key: emails})
        r = requests.delete(api_url(endpoint), data=request_data, headers=header)
        if handle_http_error(r):
            return

        # mark emails as unsubscribed in erpnext
        for email in emails:
            global_unsubscribe_and_commit(email)
    else:
        # perform deletion request for each email
        for email in emails:
            global_unsubscribe_and_commit(email)

            # remove from SendGrid list
            email_removal_url = "{}/{}".format(remove_endpoint.rstrip("/"),
                                               urllib.quote_plus(email))
            r = requests.delete(api_url(email_removal_url), headers=header)

            # check if rate limit reached
            if r.status_code == 429:
                msg = "SendGrid request rate limit reached for {}".format(
                    remove_endpoint)
                frappe.errprint(msg)
                break

            # process errors
            if handle_http_error(r):
                continue
