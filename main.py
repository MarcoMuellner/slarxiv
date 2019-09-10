# django initial stuff
import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.core.wsgi import get_wsgi_application
get_wsgi_application()
#library imports
import json
from tangerine import Tangerine
import arxiv
from django.utils.timezone import now
from datetime import timedelta
from pandas import DataFrame as df
from db.models import User
from time import sleep

# Ensure settings are read
application = get_wsgi_application()
path = os.path.dirname(os.path.realpath(__file__)) + "/"

with open(f'{path}secret.json', 'r') as f:
    d = json.load(f)

tangerine = Tangerine(d['slack-secret'])

def get_arxiv_news(query_string,filter_list = None):
    result = arxiv.query(query=query_string,
                         sort_by="lastUpdatedDate",
                         sort_order="descending",
                         prune=True,
                         iterative=True,
                         max_chunk_results=50,
                         max_results=250)
    time =now().replace(hour=18,minute=0,second=0,microsecond=0)

    lower_time = time - timedelta(days=4) if time.weekday() == 1 else time - timedelta(days=2)
    upper_time = time - timedelta(days=1)

    paper_dict = {
        'title' : [],
        'summary' : [],
        'author' : [],
        'link' : [],
        'date' : [],
        'obj' : []
    }
    for i in result():
        paper_time = now().replace(year=i['updated_parsed'][0], month=i['updated_parsed'][1],
                                   day=i['updated_parsed'][2], hour=i['updated_parsed'][3],
                                   minute=i['updated_parsed'][4])
        if filter_list is not None:
            filtered = False
            for j in filter_list.split(";"):
                if j in i['summary']:
                    filtered = True
            if filtered:
                continue

        if lower_time < paper_time < upper_time:
            author_str = ""
            for j in i.authors:
                author_str += f"{j}, "
            paper_dict['title'].append(i['title'].replace('\n',''))
            paper_dict['summary'].append(i['summary'])
            paper_dict['author'].append(author_str)
            paper_dict['link'].append(i['arxiv_url'])
            paper_dict['date'].append(paper_time)
            paper_dict['obj'].append(i)
        else:
            break

    return df.from_dict(paper_dict)

@tangerine.listen_for('add category')
def add_category(user, message):
    try:
        u = User.objects.get(u_id=user)
    except User.DoesNotExist:
        u = User(u_id=user)
        u.save()

    channel = user
    if u.categories is None:
        u.categories = message.split(" ")[-1].split("|")[-1][:-1]
    else:
        u.categories += ";" +  message.split(" ")[-1].split("|")[-1][:-1]
    u.save()
    tangerine.speak(f"Set up categories: {u.categories}",channel)

@tangerine.listen_for('add filter')
def add_category(user, message):
    try:
        u = User.objects.get(u_id=user)
    except User.DoesNotExist:
        u = User(u_id=user)
        u.save()

    channel = user
    if u.filter_list is None:
        u.filter_list = message.replace("add filter ","")
    else:
        u.filter_list += ";" +  message.replace("add filter ")[-1]
    u.save()
    tangerine.speak(f"Set up filter: {u.filter_list}",channel)

@tangerine.listen_for('personal')
def personal_news(user, message):
    try:
        u = User.objects.get(u_id=user)
    except User.DoesNotExist:
        u = User(u_id=user)
        u.save()

    channel = user
    if u.categories is None:
        tangerine.speak("You need to set up categories. Type 'add category CATEGORY'. Categories must be named in"
                        "arxiv format.",channel)
        return

    cat_text = ""
    try:
        for i in u.categories.split(";")[:-1]:
            cat_text += "cat:" + i + " OR"
    except IndexError:
        cat_text = ""
    cat_text += "cat:" + u.categories.split(";")[-1]
    papers = get_arxiv_news(cat_text,u.filter_list)

    for i in papers.sort_values(by=['date'],ascending=False).iterrows():
        i = i[1]
        text = f"*{i.title}* ({i.date.strftime('%d.%m.%Y: %H:%M')})\n"
        text += f"*Author(s): {i.author} *\n\n"
        text += f">>>{i.summary}\n\n"
        text += f"*Link: {i.link} *"
        tangerine.speak(text, channel)
        sleep(0.1)

@tangerine.listen_for('news')
def news(user, message):
    papers = get_arxiv_news("cat:astro-ph.SR OR cat:astro-ph.IM OR astro-ph.EP")

    channel = "#arxiv"

    for i in papers.sort_values(by=['date'],ascending=False).iterrows():
        i = i[1]
        text = f"*{i.title}* ({i.date.strftime('%d.%m.%Y: %H:%M')})\n"
        text += f"*Author(s): {i.author} *\n\n"
        text += f">>>{i.summary}\n\n"
        text += f"*Link: {i.link} *"
        tangerine.speak(text, tangerine.get_channel_id_from_name(channel))
        sleep(0.1)

if __name__ == '__main__':
   tangerine.run()