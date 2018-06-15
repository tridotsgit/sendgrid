from __future__ import unicode_literals
import frappe

def after_install():
	"""Add SendGrid under Email Account Service options"""
	meta = frappe.get_meta("Email Account")
	options = filter(None, meta.get_field("service").options.split("\n"))
	options.append("SendGrid")
	options = [""] + sorted(list(set(options)))
	frappe.make_property_setter({
		"doctype": "Email Account",
		"fieldname": "service",
		"property": "options",
		"value": "\n".join(options),
		"property_type": "Text"
	})
