from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings

def link_callback(uri, rel):
    """
    Tukar URI HTML (contoh: /static/...) kepada laluan sistem fail mutlak
    supaya xhtml2pdf boleh mengakses fail-fail imej dan CSS.
    """
    static_url = settings.STATIC_URL    # Biasanya '/static/'
    static_root = settings.STATIC_ROOT  # Lokasi folder 'staticfiles'
    media_url = settings.MEDIA_URL      # Biasanya '/media/'
    media_root = settings.MEDIA_ROOT    # Lokasi folder 'media'

    if uri.startswith(static_url):
        path = os.path.join(static_root, uri.replace(static_url, ""))
    elif uri.startswith(media_url):
        path = os.path.join(media_root, uri.replace(media_url, ""))
    else:
        return uri  # Kembalikan URI asal jika ia pautan luaran (http://...)

    # Pastikan fail wujud
    if not os.path.isfile(path):
        raise Exception(f'Fail tidak dijumpai: {path}')
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    
    # Luluskan link_callback kepada pisaDocument
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result, 
        encoding='UTF-8',
        link_callback=link_callback
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None