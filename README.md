## SendGrid Integration

Set communication status from SendGrid via webhooks.

### Installation

1. Install [Frappe Bench](https://github.com/frappe/bench)
1. Get SendGrid Integration App: `bench get-app sendgrid_integration https://github.com/semilimes/sendgrid_integration`
1. Install it for your site: `bench --site {site_name} install-app sendgrid_integration`
1. Restart your bench

### How To Use

1. Create [SendGrid](www.sendgrid.com) account
1. Go to [API Keys](https://app.sendgrid.com/settings/api_keys) settings and generate API Key
	- Give full access to 'Event Notification' and 'Mail Send'
1. Use your SendGrid credentials and API Key to setup Email Account in Frappe
	- Check 'Login ID is different' and use your Sendgrid username as Login ID
1. SendGrid event webhook will be configured automatically if Email Account settings are correct
1. You can double check webhook settings in [Mail Settings](https://app.sendgrid.com/settings/mail_settings)

### License

MIT

#### Developed by [Semilimes](www.semilimes.com), all@semilimes.com
