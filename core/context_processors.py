from groups.models import Group, GroupJoinRequest
from notifications.models import Notification



def dashboard_counters(request):
    if request.user.is_authenticated:
        counters = {}

        if request.user.role == 'organizer':
            counters['group_count'] = Group.objects.filter(created_by=request.user).count()
            counters['pending_requests'] = GroupJoinRequest.objects.filter(
                group__created_by=request.user, status='unread'
            ).count()

        # notifiche non lette per qualsiasi ruolo
        counters['unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).exclude(
            match__score_team1__isnull=False,
            match__score_team2__isnull=False
        ).count()

        return counters
    return {}
