import hashlib
import time
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

IMAGE_BASE_DIR = "/home/evan/articles/images/images/"
MAX_IMAGE_SIZE = 1024 * 1024  # 1MB


@csrf_exempt
def image_upload(request):

    upload_result = {
        'success': 0,
        'message': "",
        'url': ""
    }

    image_file = request.FILES.get("editormd-image-file")
    image_file_size = image_file.size

    if image_file_size > MAX_IMAGE_SIZE:
        upload_result['message'] = "上传图片大小不能超过１Ｍ！"
        return HttpResponse(json.dumps(upload_result))

    image_file_type = image_file.name.split('.')[-1]
    image_id = __create_id()
    image_path = IMAGE_BASE_DIR + image_id + "." + image_file_type
    try:
        __handle_uploaded_file(image_file, image_path)
    except:
        upload_result['message'] = "上传失败！"
        return HttpResponse(json.dumps(upload_result))

    upload_result['success'] = 1
    upload_result['message'] = "上传成功！"
    upload_result['url'] = "/static/images/" + image_id + "." + image_file_type
    return HttpResponse(json.dumps(upload_result))


def __handle_uploaded_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def __create_id():
    m = hashlib.md5(str(time.clock()).encode('utf-8'))
    return m.hexdigest()
