from django import template
from django.utils.safestring import mark_safe

from shopping.models import Brand

register = template.Library()


@register.simple_tag
def Brands():
    items = Brand.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li><a href="/Brands/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)

@register.simple_tag
def Brands_mobile():
    items = Brand.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li class="item-menu-mobile"><a href="/Brands/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)


@register.simple_tag
def Brands_li_a():
    items = Brand.objects.filter(is_active=True).order_by('title')
    items_li_a = ""
    for i in items:
        items_li_a += """<li class="p-t-4"><a href="/Brands/{}" class="s-text13">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li_a)


@register.simple_tag
def Brands_div():
    """
    section banner
    :return:
    """
    items = Brand.objects.filter(is_active=True).order_by('title')
    items_div = ""
    item_div_list = ""
    for i, j in enumerate(items):
        if not i % 2:
            items_div += """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/Brand/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
        else:
            items_div_ = """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/Brand/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
            item_div_list += """<div class="col-sm-10 col-md-8 col-lg-4 m-l-r-auto">""" + items_div + items_div_ + """</div>"""
            items_div = ""

    return mark_safe(item_div_list)