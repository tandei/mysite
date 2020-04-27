from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def SuccessResponse(like_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = like_num
    return JsonResponse(data)

def like_change(request):
    #获取数据
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(4000, '还没登录呢')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(4040, '对象不存在')

    if request.GET.get('is_like') == 'true':
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            #已点赞
            return ErrorResponse(4002, '已点赞咯')
    else:
        if LikeRecord.objects.filter(content_type=content_type,object_id=object_id,user=user).exists():
            like_record = LikeRecord.objects.get(content_type=content_type,object_id=object_id,user=user)
            like_record.delete()
            #点赞总数减1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(4004, '数据错误了呀')
        else:
            #没有点赞过，不可取消，重复取消
            return ErrorResponse(4003, '还没点赞呢')