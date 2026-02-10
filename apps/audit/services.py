import threading

_thread_local = threading.local()


def get_request_metadata():
    return {
        "ip_address": getattr(_thread_local, "ip_address", None),
        "user_agent": getattr(_thread_local, "user_agent", ""),
    }


def set_request_metadata(ip_address, user_agent):
    _thread_local.ip_address = ip_address
    _thread_local.user_agent = user_agent


def log_audit_event(user, action, entity_type, entity_id, details=None):
    from apps.audit.models import AuditLog

    meta = get_request_metadata()
    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details,
        ip_address=meta["ip_address"],
        user_agent=meta["user_agent"],
    )
