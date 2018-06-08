from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "sendgrid-integration",
					"label": "SendGrid Integration",
					"description": _("How to integrate email status with SendGrid"),
				},
			]
		}
	]
