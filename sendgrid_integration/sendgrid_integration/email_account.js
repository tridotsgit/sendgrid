$.extend(frappe.email_defaults, {
	"SendGrid": {
		"enable_outgoing": 1,
		"smtp_server": "smtp.sendgrid.net",
		"smtp_port": 587,
		"use_tls": 1
	}
});

frappe.ui.form.on("Email Account", {
	refresh: function(frm) {
		frm.dashboard.reset();
		if (frm.doc.sendgrid_webhook_credentials) {
			frm.dashboard.set_headline_alert(__("SendGrid integration is active"), "alert-default");
		}
	}
})
