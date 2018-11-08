from django import forms
from django_comments.forms import CommentForm

from captcha.fields import CaptchaField
from crequest.middleware import CrequestMiddleware


class MPTTCommentForm(CommentForm):
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None, parent_id=None, **kwargs):
        if initial is None:
            initial = {}
        initial.update({'parent_id': parent_id})
        super(MPTTCommentForm, self).__init__(target_object, data=data, initial=initial, **kwargs)

        current_request = CrequestMiddleware.get_request()
        if current_request.user.is_authenticated:
            self.fields['email'].required = False
            self.fields['name'].required = False
        else:
            self.fields['captcha'] = CaptchaField()

    def get_comment_create_data(self, **kwargs):
        data = super(MPTTCommentForm, self).get_comment_create_data(**kwargs)
        data['parent_id'] = self.cleaned_data.get('parent_id')
        return data
