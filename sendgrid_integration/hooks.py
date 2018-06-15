# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "sendgrid_integration"
app_title = "SendGrid Integration"
app_publisher = "Semilimes Ltd."
app_description = "Set communication status from SendGrid via webhooks"
app_icon = "octicon octicon-inbox"
app_color = "#4CB6E6"
app_email = "all@semilimes.com"
app_version = "0.0.1"

fixtures = ["Custom Field"]
clear_cache = "sendgrid_integration.account.clear_cache"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sendgrid_integration/css/sendgrid_integration.css"
# app_include_js = "/assets/sendgrid_integration/js/sendgrid_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/sendgrid_integration/css/sendgrid_integration.css"
# web_include_js = "/assets/sendgrid_integration/js/sendgrid_integration.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#   "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sendgrid_integration.install.before_install"
after_install = "sendgrid_integration.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sendgrid_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#   "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#   "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#   "*": {
#       "on_update": "method",
#       "on_cancel": "method",
#       "on_trash": "method"
#   }
# }

doc_events = {
    "Email Account": {
        "on_update": "sendgrid_integration.webhooks.sync"
    }
}

doctype_js = {
    "Email Account": "sendgrid_integration/email_account.js"
}

make_email_body_message = "sendgrid_integration.webhook_events.set_meta_in_email_body"

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "all": [
    #   "sendgrid_integration.tasks.all"
    # ],
    "daily": [
        "sendgrid_integration.blacklist.unsubscribe_blacklisted"
    ],
    # "hourly": [
    #   "sendgrid_integration.tasks.hourly"
    # ],
    # "weekly": [
    #   "sendgrid_integration.tasks.weekly"
    # ]
    # "monthly": [
    #   "sendgrid_integration.tasks.monthly"
    # ]
}

# Testing
# -------

# before_tests = "sendgrid_integration.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#   "frappe.desk.doctype.event.event.get_events": "sendgrid_integration.event.get_events"
# }
