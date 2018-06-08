# -*- coding: utf-8 -*-
# Copyright (c) 2016, Semilimes
# MIT License. See license.txt

import json
import base64

import frappe

from .account import set_status, get_webhook_credentials


@frappe.whitelist(allow_guest=True, xss_safe=True)
def notify(sendgrid_events=None):
    """
    Method for SendGrid Event webhook.

    SendGrid  will call this public method to notify about status changes of sent mail.

    JSON data example from https://sendgrid.com/docs/API_Reference/Webhooks/event.html

    [
        {
            "sg_message_id":"sendgrid_internal_message_id",
            "email": "john.doe@sendgrid.com",
            "timestamp": 1337197600,
            "smtp-id": "<4FB4041F.6080505@sendgrid.com>",
            "event": "processed"
        },
        {
            "sg_message_id":"sendgrid_internal_message_id",
            "email": "john.doe@sendgrid.com",
            "timestamp": 1337966815,
            "category": "newuser",
            "event": "click",
            "url": "https://sendgrid.com"
        },
        {
            "sg_message_id":"sendgrid_internal_message_id",
            "email": "john.doe@sendgrid.com",
            "timestamp": 1337969592,
            "smtp-id": "<20120525181309.C1A9B40405B3@Example-Mac.local>",
            "event": "group_unsubscribe",
            "asm_group_id": 42
        }
    ]

    + every event will have additional argument 'message_id' with local message ID
    """
    if not frappe.request:
        return

    if not authenticate_credentials():
        raise frappe.AuthenticationError

    try:
        sendgrid_events = json.loads(frappe.request.data) or []
        for event in sendgrid_events:
            set_status(event.get("event"), event.get("email"), event.get("message_id"))
    except ValueError:
        frappe.errprint("Bad SendGrid webhook request")


def authenticate_credentials():
    """
    Process Authorization header in HTTP response according to basic HTTP authorization.

    Request is stored as Werkzeug local, frappe provides access to headers.
    """
    received_credentials = frappe.get_request_header("Authorization")

    # seems like a dummy post request
    if not received_credentials:
        return False

    # invalid HTTP basic authorization header
    if not received_credentials.startswith("Basic"):
        return False

    splitted_credentials = received_credentials.split(" ", 1)
    if len(splitted_credentials) != 2:
        frappe.errprint("SendGrid webhook authentication failed with header: {}".format(
            received_credentials))
        return False

    received_credentials = splitted_credentials[1]
    for credentials in get_webhook_credentials():
        # matched => authenticated
        if received_credentials == base64.b64encode(credentials):
            return True

    # no match => failure
    return False


def set_meta_in_email_body(email):
    """
    Set X-SMTPAPI header in email to add unique arguments to email message.

    Additional argument with message id allows to track this particular message in
    events from event webhook. Called via app hook make_email_body_message.

    :param email: Email Account doctype to take message id from
    """
    message_id = email.msg_root.get("Message-Id")
    if message_id:
        args = {"unique_args": {"message_id": message_id}}
        email.msg_root[b'X-SMTPAPI'] = json.dumps(args)
