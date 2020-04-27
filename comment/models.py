import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class SendMail(threading.Thread):
    def __init__(self, subject, text, host_user, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.host_user = host_user
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject, 
            '', 
            self.host_user, 
            [self.email], 
            fail_silently=self.fail_silently,
            html_message=self.text
        )


# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') #TODO

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)

    def send_email(self):
        if self.parent is None:
            # 评论我的博客
            subject = '博客被评论'
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '评论被回复'
            email = self.reply_to.email
        if email != '':
            host_user = settings.EMAIL_HOST_USER
            #text = '%s\n<a href="%s">%s</a>' % (self.text, '\n' + self.content_object.get_url(), '点击查看')
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_mail.html', context)
            #import pdb
            #pdb.set_trace()
            send_mail = SendMail(subject, text, host_user, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']




