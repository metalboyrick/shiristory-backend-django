import errno
import os
import time

from PIL import Image
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.core.files.storage import FileSystemStorage

from shiristory.settings import BASE_DIR


def random_string(length=64):
    return BaseUserManager() \
        .make_random_password(length=length,
                              allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ1234567890')


def check_missing_fields(contents, fields: list):
    missing_fields = {}
    for field in fields:
        if field not in contents:
            missing_fields[field] = ['This field is required.']
    if len(missing_fields) >= 1:
        return missing_fields
    else:
        return None


def timestamp_filename(file_name, file_extension):
    return f'{file_name}_{int(round(time.time() * 1000))}.{file_extension}'


def save_uploaded_medias(request, upload_to):
    """
    @return: An array of images' absolute url if success, False if fail
    """

    # /media/
    k_media_url = settings.MEDIA_URL
    # BASE_DIR/media/
    k_media_root = settings.MEDIA_ROOT
    # http://website.com
    k_app_url = settings.APP_URL
    # 80
    k_app_port = settings.APP_PORT

    result = []

    try:
        save_file_dir = os.path.join(k_media_root, upload_to)
        if not os.path.exists(save_file_dir):
            os.makedirs(save_file_dir)
        file_system = FileSystemStorage(location=save_file_dir)

        for filename, file in request.FILES.items():
            # Save media
            save_file_name = timestamp_filename(random_string(5), filename.split('.')[-1])
            file_system.save(save_file_name, file)
            file_abs_url = f'{k_app_url}:{k_app_port}{k_media_url}{upload_to}/{save_file_name}'

            result.append(file_abs_url)

        return result

    except (ValueError, OSError) as error:
        print(f'Save Media Error: {error}')
        raise Exception(f'Save Media Error: {error}')


# file_path example:
# /media/lost_notice_images/id_1_1605532600500.jpg
def delete_media_file(file_path):
    # Remove initial '/' in file path
    path = os.path.join(BASE_DIR, file_path[1:])
    # Silent remove
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:  # e
            # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


# url example:
# http://website.com/media/folder/id_1_1605532600500.jpg
# MEDIA_URL: /media/
def delete_media_from_url(url):
    start_index = url.find(settings.MEDIA_URL)
    delete_media_file(url[start_index:])


def delete_instance_medias(instance, media_attributes, json=False):
    # Handle single attribute
    if type(media_attributes) not in [list, tuple]:
        media_attributes = [media_attributes]

    for attribute in media_attributes:
        if not json:
            media_field = getattr(instance, attribute)
            if media_field:
                file_path = media_field.url
                delete_media_file(file_path)
        else:
            image_abs_urls = getattr(instance, attribute)
            if not image_abs_urls:
                return
            # image_abs_urls = image_abs_urls['image_urls']
            for image_abs_url in image_abs_urls:
                url = image_abs_url['url']
                delete_media_from_url(url)
