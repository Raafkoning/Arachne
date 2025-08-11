import json

from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render
from urllib.parse import unquote

from .models import *
from .utils import *
from background_task.models import Task
from static.libs import exceptions as exc

#Main view
def scrape(request):

    if request.method == "POST":
        url = request.POST.get('url', '')

        try:
            Validate.URL(url)
        except exc.URLError as e:
            return error(request, e)

        

        scrape_items(url)

        task = Task.objects.filter(task_name='istos.utils.scrape_items').last()

        request.session['task_id'] = task.id

        return redirect('/loading/first/')

    data = Link.objects.all().order_by('id')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data, 15)

    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {'data': page_obj})

#scraping link from another link
def sec_scrape(request, id, url):
    d_url = unquote(url)
    scrape_items(d_url)

    task = Task.objects.filter(task_name='istos.utils.scrape_items').last()

    request.session['task_id'] = task.id
    request.session['parent_id'] = id
    
    return redirect('/loading/second/')
    
#updating link that has been scraped
def update(request, url):
    d_url = unquote(url).rstrip('/') + '/'
    scrape_items(d_url)

    print(d_url)

    curr_link = Link.objects.get(url=d_url)
    task = Task.objects.filter(task_name='istos.utils.scrape_items').last()

    request.session['task_id'] = task.id
    request.session['curr_id'] = curr_link.id

    return redirect('/loading/update/')

#delete one item/link from DB
def delete(request,type, id):
    previous_url = request.META.get('HTTP_REFERER')
    match(type):
        case "Link":
            Link.objects.filter(id=id).first().delete()
        case "Item":
            Items.objects.filter(id=id).first().delete()

    return redirect(previous_url)

#deletes all Links
def clear(request):
    Link.objects.all().delete()

    return redirect('/')

#Item page
def items(request, id):
    #for saving items to computer
    if request.method == "POST":
        ids = request.POST.get('save_form_input', '')
        parent_id = id
        
        split_ids = ids.split(',')
        choice = split_ids[0]
        del split_ids[0]
        ids = ','.join(split_ids)
            
        match choice:
            case "save":
                start_save(parent_id, ids)
                return redirect('/')
            case "delete":
                delete_items(parent_id, ids)

    items = Items.objects.filter(link_id=id).order_by('id')

    link = Link.objects.get(id=id)
    link_info = (link.url, link.title, link.id)

    data = {
        "items" : items,
        "link_info": link_info,
    }

    if link.hasParent:
        parent = link.hasParent
        parent_info = (parent.url, parent.title, parent.id)
        data["parent_info"] = parent_info
    
    return render(request, 'items.html', {'data': data})

#Settings page
def settings(request):
    if request.method == "POST":
        picformats = Formats.objects.filter(type='pic').values_list("formName", "formSave")
        vidformats = Formats.objects.filter(type='vid').values_list("formName", "formSave")
        settings = Settings.objects.exclude(id=1).values_list('settingName', 'on') 

        for pic in picformats:
            value = request.POST.get(pic[0], 'off')
            previous = pic[1]

            current = (value != 'off')

            if current != previous:
                update_db = Formats.objects.get(formName=pic[0])
                update_db.formSave = current
                update_db.save()

        for vid in vidformats:
            value = request.POST.get(vid[0], 'off')
            previous = vid[1]

            current = (value != 'off')

            if current != previous:
                update_db = Formats.objects.get(formName=vid[0])
                update_db.formSave = current
                update_db.save()

        for sett in settings:
            value = request.POST.get(sett[0], 'off')
            previous = sett[1]

            current = (value != 'off')

            if current != previous:
                update_db = Settings.objects.get(settingName=sett[0])
                update_db.on = current
                update_db.save()


        
    saveloc = Settings.objects.filter(settingName='save_loc').values_list("link", flat=True).first()

    settings_labels = ["Go To Items", "Absolute Links", "Related Links", "Relative Links"]
    settings_info = ["Automatically go to items after scraping", "Grab absolute links", "Absolute links will be related to parent", "Grab relative links"]

    settings = Settings.objects.exclude(id=1).values_list('settingName', 'on')
    picformats = Formats.objects.filter(type='pic').values_list("formName", "formSave")
    vidformats = Formats.objects.filter(type='vid').values_list("formName", "formSave")

    full_settings = [
        {
            'name': setting[0],
            'on': setting[1],
            'label': label,
            'info': info
        }
        for setting, label, info in zip(settings, settings_labels, settings_info)
    ]

    data = {
        "savelocation": saveloc,
        "settings": full_settings,
        "picformats": picformats,
        "vidformats": vidformats,
    }

    return render(request, 'settings.html', {'data': data})

#Loading page while Scraping is happening
def loading(request, type):
    parent_id = 0
    current_id = 0
    match type:
        case "first":
            h1 = "Scraping Website"
        case "second":
            parent_id = request.session.get('parent_id')
            h1 = "Scraping Website"
        case "update":
            h1 = "Updating Items"
            current_id = request.session.get('curr_id')

    link = Link.objects.last()

    #Task Info
    task_id = request.session.get('task_id')
    task_pending = Task.objects.filter(id=task_id).exists()

    #Setting
    go_to_items = Settings.objects.get(settingName = 'auto_items')

    if task_pending:
        task_params = Task.objects.filter(id=task_id).values_list('task_params', flat=True)
        request.session['task_url'] = task_params[0].split('"')[1]
        return render(request, 'loading.html', {'data': h1})
    
    if(type=="second"):
            parent_link(link.id, parent_id)

    if go_to_items.on:
        if current_id == 0:
            return redirect(f'/{link.id}')
        else:
            return redirect(f'/{current_id}')
    else:
        return get_page_num(request, current_id)

#for paginator to go to the correct page
def get_page_num(request, parent_id):
    task_url = request.session.get('task_url').rstrip('/') + '/'
    print(task_url)
    link = Link.objects.get(url=task_url)

    if(parent_id != 0):
        parent = Link.objects.get(id=parent_id)
        link.hasParent = parent
        link.save()

    link_id = link.id

    #Returns to Index if page not found
    if not link_id:
        return redirect('/')

    #Order Links by specified number
    data = Link.objects.all().order_by('id')
    paginator = Paginator(data, 15)

    #Calculate the page number of the Link
    link_ids = list(data.values_list('id', flat=True))
    print(link_ids)
    try:
        position = link_ids.index(link_id)  # 1-based position
    except ValueError:
        return redirect('/')

    page_number = (position // 15) + 1
    return redirect(f'/?page={page_number}')

#Error Page
def error(request, e):
    return render(request, 'error.html', {'data': e})


    

    

