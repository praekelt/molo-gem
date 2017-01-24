from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import MediaForm

from django.conf import settings
import shutil
import os
import zipfile
import StringIO


def handle_uploaded_file(file):
    '''Replace the Current Media Folder.'''

    print(file.name)
    print(settings.MEDIA_ROOT)

    media_parent_directory = os.path.dirname(settings.MEDIA_ROOT)
    zip_file_reference = os.path.join(media_parent_directory, 'new_media.zip')

    print("DELETING")
    # delete current media folder if it exists
    if os.path.isdir(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)

    print("COPYING THE ZIP FILE TO ROOT DIR")
    # copy the zip file to the root directory
    with open(zip_file_reference, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    print("UNZIPPING THE FILE")
    # unzip the current media file
    with zipfile.ZipFile(zip_file_reference, 'r') as z:
        z.extractall(media_parent_directory)

    print("REMOVING THE ZIP FILE")
    # delete the zip file
    os.remove(zip_file_reference)

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def upload_file(request):
    '''Upload a Zip File Containing a single file containing media.'''
    if request.method == 'POST':
        print("Confirmed: post")
        form = MediaForm(request.POST, request.FILES)
        print("Confirmed: form object created")
        if form.is_valid():
            print("form is valid")
            handle_uploaded_file(request.FILES['zip_file'])
            return HttpResponseRedirect('/django-admin/')
    else:
        form = MediaForm()
    return render(request, 'admin/upload_media.html', {'form': form})


def download_file(request):
    '''Create and download a zip file containing the media file.'''
    if request.method == "GET":
        zipfile_name = 'media_%s.zip' % settings.SITE_NAME
        in_memory_file = StringIO.StringIO()

        media_zipfile = zipfile.ZipFile(in_memory_file, 'w', zipfile.ZIP_DEFLATED)

        directory_name = os.path.split(settings.MEDIA_ROOT)[-1]
        for root, dirs, files in os.walk(directory_name):
            for file in files:
                media_zipfile.write(os.path.join(root, file))

        # Must close zip for all contents to be written
        media_zipfile.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = HttpResponse(in_memory_file.getvalue(), content_type = "application/x-zip-compressed")
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zipfile_name

        return resp
