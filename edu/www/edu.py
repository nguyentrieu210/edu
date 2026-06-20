import frappe

no_cache = 1


def get_context(context):
	# Khách chưa đăng nhập -> đẩy ra trang login, không cho ở lại SPA.
	# Dùng 302 (tạm thời) để trình duyệt không cache redirect sau khi đã đăng nhập.
	if frappe.session.user == "Guest":
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/login?redirect-to=/"
		frappe.local.response["http_status_code"] = 302
		raise frappe.Redirect

	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token
	frappe.boot.csrf_token = csrf_token
