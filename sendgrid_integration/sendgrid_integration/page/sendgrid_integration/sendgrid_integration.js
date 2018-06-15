frappe.pages['sendgrid-integration'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'SendGrid Integration',
		single_column: true
	});

	frappe.breadcrumbs.add("Integrations");

	$(frappe.render_template("permission_manager_help", {})).appendTo(page.main);
}
