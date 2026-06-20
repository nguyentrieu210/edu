import frappe

no_cache = 1


def get_context(context):
	# Cho khách (Guest) tải được SPA shell -> trang đăng nhập custom render client-side.
	# CSRF token cấp cho cả guest để POST /api/method/login hoạt động.
	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token
	frappe.boot.csrf_token = csrf_token
