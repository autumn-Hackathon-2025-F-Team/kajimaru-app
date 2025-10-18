import time

HK = 'household_id'
MK = 'active_member_id'
LS = 'profile_last_seen'

class HouseholdSessionMiddleware:
    """
    15分間アクティビティがない場合、セッションを終了するミドルウェア
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get(MK):
            last = request.session.get(LS, 0)
            now = time.time()
            if now - last > 15 * 60:
                request.session.pop(MK, None)
            else:
                request.session[LS] = now
        return self.get_response(request)
