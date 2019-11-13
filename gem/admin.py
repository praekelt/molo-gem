from collections import Counter

from django.contrib import admin
from django.contrib.auth.models import User

from gem.models import (
    GemCommentReport, OIDCSettings,
    Questionnaire, QuestionnaireChoice
)
from gem.rules import ProfileDataRule, CommentCountRule

from molo.commenting.admin import MoloCommentAdmin, MoloCommentsModelAdmin
from molo.commenting.models import MoloComment
from molo.profiles.models import UserProfile
from molo.forms.models import FormsSegmentUserGroup

from wagtail.contrib.modeladmin.helpers import PermissionHelper


class OIDCSettingsAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = "OIDC Settings"


class UserProfileInlineModelAdmin(admin.StackedInline):
    model = UserProfile
    can_delete = False


class GemCommentReportModelAdmin(admin.StackedInline):
    model = GemCommentReport
    can_delete = True
    max_num = 0
    actions = None
    readonly_fields = ["user", "reported_reason", ]


class FormsSegementUserPermissionHelper(PermissionHelper):
    def __init__(self, model, inspect_view_enabled=False):
        model = FormsSegmentUserGroup
        super(FormsSegementUserPermissionHelper, self).__init__(
            model, inspect_view_enabled
        )


class GemCommentModelAdmin(MoloCommentsModelAdmin):
    list_display = (
        'comment', 'parent_comment', 'moderator_reply', 'content', '_user',
        'is_removed', 'is_reported', 'reported_count', 'reported_reason',
        'submit_date', 'country')

    def reported_reason(self, obj):
        all_reported_reasons = list(
            GemCommentReport.objects.filter(comment=obj.pk).values_list(
                'reported_reason', flat=True))
        breakdown_of_reasons = []
        for value, count in Counter(all_reported_reasons).most_common():
            reason = '%s, (%s)' % (value, count)
            breakdown_of_reasons.append(reason)

        return breakdown_of_reasons

    def reported_count(self, obj):
        return GemCommentReport.objects.filter(comment=obj.pk).count()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


class ProfileDataRuleAdminInline(admin.TabularInline):
    """
    Inline the ProfileDataRule into the administration
    interface for segments.
    """
    model = ProfileDataRule


class CommentCountRuleAdminInline(admin.TabularInline):
    """
    Inline the CommentCountRule into the administration
    interface for segments.
    """
    model = CommentCountRule


class QuestionnaireChoiceAdminInline(admin.TabularInline):
    model = QuestionnaireChoice


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("questionnaire_text", "pub_date")
    inlines = [QuestionnaireChoiceAdminInline]


admin.site.unregister(User)
admin.site.unregister(MoloComment)
admin.site.register(OIDCSettings, OIDCSettingsAdmin)
admin.site.register(MoloComment, GemCommentReportAdmin)
admin.site.register(Questionnaire, QuestionnaireAdmin)
