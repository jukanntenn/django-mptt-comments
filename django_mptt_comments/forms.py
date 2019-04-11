from captcha.fields import CaptchaField
from crequest.middleware import CrequestMiddleware
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_comments.forms import COMMENT_MAX_LENGTH, CommentForm

from .models import MPTTComment


class MPTTCommentForm(CommentForm):
    parent_comment_pk = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None, parent_comment_pk=None,
                 **kwargs):
        if initial is None:
            initial = {}
        initial.update({'parent_comment_pk': parent_comment_pk})
        super(MPTTCommentForm, self).__init__(target_object, data=data,
                                              initial=initial, **kwargs)

        current_request = CrequestMiddleware.get_request()
        if current_request.user.is_authenticated:
            self.fields['email'].required = False
            self.fields['name'].required = False
        else:
            self.fields['captcha'] = CaptchaField()

    def get_comment_create_data(self, **kwargs):
        data = super(MPTTCommentForm, self).get_comment_create_data(**kwargs)
        data['parent_comment_pk'] = self.cleaned_data.get('parent_comment_pk')
        return data


class CommentEditForm(forms.ModelForm):
    comment = forms.CharField(label=_('Comment'), widget=forms.Textarea, max_length=COMMENT_MAX_LENGTH)

    class Meta:
        model = MPTTComment
        fields = ['comment']
