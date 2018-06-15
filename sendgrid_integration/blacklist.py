# -*- coding: utf-8 -*-
# Copyright (c) 2016, Semilimes
# For license information, please see license.txt

import frappe

from .sendgrid import unsubscribe_emails


def unsubscribe_blacklisted():
    """
    Get blacklisted emails, unsubscribe them globally and delete them from SendGrid.

    Run via Daily Scheduler.
    """
    for email_account in frappe.get_all("Email Account",
                                        filters={"service": "SendGrid",
                                                 "enable_outgoing": 1},
                                        fields=["api_key",
                                                "sendgrid_webhook_credentials"]):

        # don't do it when SendGrid integration is inactive
        if not email_account.sendgrid_webhook_credentials or not email_account.api_key:
            continue

        # process blocked emails
        unsubscribe_emails(email_account.api_key,
                           endpoint="/suppression/blocks")

        # process bounced emails
        unsubscribe_emails(email_account.api_key,
                           endpoint="/suppression/bounces")

        # process emails that were marked as spam
        unsubscribe_emails(email_account.api_key,
                           endpoint="/suppression/spam_reports")

        # process invalid emails
        unsubscribe_emails(email_account.api_key,
                           endpoint="/suppression/invalid_emails")

        # process unsubscribed emails
        unsubscribe_emails(email_account.api_key,
                           endpoint="/suppression/unsubscribes",
                           remove_endpoint="/asm/suppressions/global",
                           batch_key=None)
