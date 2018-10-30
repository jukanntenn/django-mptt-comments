from django import forms
from django_comments.forms import CommentForm

from captcha.fields import CaptchaField
from crequest.middleware import CrequestMiddleware


class MPTTCommentForm(CommentForm):
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None, parent=None, **kwargs):
        self.user = kwargs.pop('user', None)
        self.parent = parent
        if initial is None:
            initial = {}
        initial.update({'parent': self.parent})
        super(MPTTCommentForm, self).__init__(target_object, data=data, initial=initial, **kwargs)
        if self.user is not None:
            if self.user.is_authenticated:
                self.fields['email'].required = False
                self.fields['name'].required = False
            else:
                self.fields['captcha'] = CaptchaField()
        else:
            current_request = CrequestMiddleware.get_request()
            if current_request.user.is_authenticated:
                self.fields['email'].required = False
                self.fields['name'].required = False
            else:
                self.fields['captcha'] = CaptchaField()

    def get_comment_create_data(self, **kwargs):
        data = super(MPTTCommentForm, self).get_comment_create_data(**kwargs)
        parent = self.cleaned_data.get('parent')
        data['parent_id'] = parent
        return data
