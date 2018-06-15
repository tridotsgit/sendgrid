# -*- coding: utf-8 -*-
# Copyright (c) 2016, Semilimes
# For license information, please see license.txt

import os
import string
import random

import frappe
from frappe.utils import get_url

from .sendgrid import webhook_exists, add_webhook
from .account import clear_cache


def sync(doc, method=None):
    """Sync Webhook under SendGrid account."""
    if not doc.service == "SendGrid":
        return

    if not (doc.api_key and
            doc.enable_outgoing and
            doc.smtp_server and
            doc.email_id and
            doc.password):
        frappe.msgprint("Imposible to setup SendGrid webhook (incorrect of settings)")
        return

    webhook_url = None
    if doc.sendgrid_webhook_credentials:
        webhook_url = get_webhook_post_url(doc.sendgrid_webhook_credentials)
        if webhook_exists(doc.api_key, webhook_url):
            frappe.msgprint("SendGrid events webhook already exists")
            return

    credentials = generate_credentials()
    webhook_url = get_webhook_post_url(credentials)
    if add_webhook(doc.api_key, webhook_url):
        # save webhook credentials in Email Account
        doc.sendgrid_webhook_credentials = credentials
        doc.db_set("sendgrid_webhook_credentials", credentials)
        frappe.db.commit()

        frappe.msgprint("SendGrid events webhook created successfuly")
    else:
        frappe.msgprint("Failed to create SendGrid events webhook")
        frappe.errprint("Failed to create SendGrid events webhook")

    # always clear key cache
    clear_cache()


def get_webhook_post_url(webhook_credentials):
    """
    Get Post URL to be called by SendGrid Webhook.

    :param webhook_credentials: 'username:password' for SendGrid event webhook
    """
    protocol, hostname = get_url().rsplit("//", 1)
    url = "{}//{}@{}".format(protocol, webhook_credentials, hostname)
    return os.path.join(url,
                        "api",
                        "method",
                        "sendgrid_integration.webhook_events.notify")


def generate_credentials():
    """Generate username and password in format 'username:password'."""
    return "{}:{}".format(generate_string(), generate_string())


def generate_string(length=10):
    """
    Generate string of random symbols and digits.

    :param length: length of string to generate
    """
    symbols = string.ascii_letters + string.digits
    return "".join((random.choice(symbols) for i in xrange(length)))
