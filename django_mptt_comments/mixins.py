from django.contrib.auth.mixins import AccessMixin
from .conf import settings


class ConditionalLoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not settings.ANONYMOUS_COMMENT_ALLOWED:
            if not request.user.is_authenticated:
                return self.handle_no_permission()

        return super(ConditionalLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
