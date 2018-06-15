# -*- coding: utf-8 -*-
# Copyright (c) 2016, Semilimes
# For license information, please see license.txt

import frappe


UNSUBSCRIBE_LABELS = ("spam_report",
                      "bounce",
                      "unsubscribe")

EVENT_TYPES = {"delivered": "Sent",
               "group_unsubscribe": "Recipient Unsubscribed",
               "spamreport": "Marked As Spam",
               "bounce": "Bounced",
               "deferred": "Delayed",
               "unsubscribe": "Recipient Unsubscribed",
               "processed": "Sent",
               "open": "Opened",
               "click": "Clicked",
               "dropped": "Rejected",
               }


def set_status(event_type, email, message_id):
    """
    Find the communication using message id and set delivery status.

    :param event_type: SendGrid event type received from webhook request
    :param email: email address received from webhook request
    :param message_id: unuque message id received from webhook request
    """
    communication = get_communication(message_id)

    if communication:

        # delivery status should be set as per the original recipient of communication
        if email in communication.recipients:
            set_delivery_status_and_commit(communication, event_type)

            if event_type in UNSUBSCRIBE_LABELS:
                global_unsubscribe_and_commit(email)


def get_communication(message_id):
    """
    Extract message id from metadata and return communication doc.

    :param message_id: unuque message id received from webhook request
    """
    if message_id and "@{site}".format(site=frappe.local.site) in message_id:
        communication_name = message_id.strip(" <>").split("@", 1)[0]
        return frappe.get_doc("Communication", communication_name)


def set_delivery_status_and_commit(communication, event_type):
    """
    Evaluate event type and set the delivery status of the communication.

    :param communication: Frappe Communication DocType
    :param event_type: SendGrid event type received from webhook request
    """
    delivery_status = EVENT_TYPES.get(event_type)

    if delivery_status:
        communication.db_set("delivery_status", delivery_status)
        frappe.db.commit()


def get_webhook_credentials():
    """
    Get SendGrid webhook credentials for all existing Email Accounts.

    Credentials are stored in cache, generator method will be provided otherwise.
    """
    def _get_webhook_credentials():
        """
        Get list of SendGrid webhook credentials for all Email Accounts.

        Generator method that gets values from db.
        """
        email_accounts = frappe.get_all("Email Account",
                                        fields=["sendgrid_webhook_credentials",
                                                "api_key"],
                                        filters={"enable_outgoing": 1,
                                                 "service": "SendGrid"})
        webhook_credentials = list()
        for account in email_accounts:
            if account.sendgrid_webhook_credentials and account.api_key:
                webhook_credentials.append(account.sendgrid_webhook_credentials)

        if frappe.conf.sendgrid_webhook_credentials:
            webhook_credentials.append(
                frappe.conf.sendgrid_webhook_credentials)

        return webhook_credentials

    return frappe.cache().get_value("sendgrid_webhook_credentials_list",
                                    generator=_get_webhook_credentials)


def clear_cache():
    """Remove SendGrid webhook credentials from cache."""
    frappe.cache().delete_value("sendgrid_webhook_credentials_list")


def global_unsubscribe_and_commit(email):
    """Set Global Unsubscribe flag for the email and commit to db.

    :param email: email address to unsubscribe
    """
    try:
        unsubscribe_data = {"doctype": "Email Unsubscribe",
                            "email": email,
                            "global_unsubscribe": 1}
        frappe.get_doc(unsubscribe_data).insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        pass
    else:
        frappe.db.commit()
