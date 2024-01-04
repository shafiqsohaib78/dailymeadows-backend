import random
import string
from django.utils.text import slugify
from langdetect import detect
from random import randint


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def random_string_generator_username(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        lang=detect(instance.title)
        if lang!='ur' and lang!='ar' and lang!='dv' and lang!='he' and lang!='ar' and lang!='ff' and lang!='ku' and lang!='my' and lang!='fa' and lang!='hy' and lang!='az':
            slug = slugify(instance.title)
        else:
            slug=slugify(random_string_generator(size=8))

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=8)
                )
        # print(new_slug)
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

def unique_username_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    # print(instance.email.split('@')[0])
    if new_slug is not None:
        username = new_slug
    else:
        email=instance.email.split('@')[0]
        username = slugify(email)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(username=username).exists()
    if qs_exists:
        new_slug = "{username}{randstr}".format(
                    username=username,
                    randstr=random_string_generator_username(size=4)
                )
        # print(new_slug)
        return unique_username_generator(instance, new_slug=new_slug)
    return username


def unique_id_generator(instance, _id=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if _id is not None:
        id1 = _id
    else:
        # print(slugify("id"))
        id1=slugify("id").upper()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(unique_id=id1).exists()
    if qs_exists:
        _id = "{id1}{randstr}".format(
                    id1=id1.upper(),
                    randstr=random_string_generator(size=18).upper()
                )
        # print("if",_id)
        return unique_id_generator(instance, _id=_id)
    _id = "{id1}{randstr}".format(
                    id1=id1.upper(),
                    randstr=random_string_generator(size=18).upper()
                )
    return _id