import time

class HouseholdSessionMiddleware:
    """
    15分間アクティビティがない場合、セッションを終了するミドルウェア
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        key_active = "active_member_id"
        key_seen = "profile_last_seen"

        if request.session.get(key_active):
            last = request.session.get(key_seen, 0)
            now = time.time()
            if now - last > 15 * 60:
                request.session.pop(key_active, None)
            else:
                request.session[key_seen] = now
        return self.get_response(request)
