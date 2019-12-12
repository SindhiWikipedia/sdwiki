#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Reza(User:reza1615), 2011
# Distributed under the terms of MIT License (MIT)
#
# for more information see [[fa:ویکی‌پدیا:درخواست‌های ربات/رده همسنگ]] and [[fa:ویکی‌پدیا:رده‌دهی مقالات همسنگ]]

from pywikibot import config
from pywikibot import pagegenerators
import re
import sys
import durusti_core
import pywikibot
import codecs
import string
import time
import MySQLdb
_cache = {}
page_list_run = []
#-----------------------------------------------version-----------------------------------------
fa_site = pywikibot.Site('sd', 'wikipedia')
en_site = pywikibot.Site('en', 'wikipedia')
versionpage = pywikibot.Page(fa_site, u'صارف:ZumrahBot/مساوی زمرہ جات/نسخہ')
lastversion = versionpage.get().strip()
version = u'30'
new_edition = u'1'
if lastversion != version:
    pywikibot.output(u"\03{lightred}Your bot dosen't use the last verion please update me!\03{default}")
    pywikibot.stopme()
    sys.exit()
#-----------------------------------------------------------------------------------------------

def namespacefinder(enlink, site):
    if _cache.get(tuple([enlink, site, 'ns'])):
        return _cache[tuple([enlink, site, 'ns'])]
    try:
        enlink = unicode(str(enlink), 'UTF-8').replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    except:
        enlink = enlink.replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    enlink = enlink.replace(u' ', u'_')
    params = {
        'action': 'query',
        'prop': 'langlinks',
        'titles': enlink,
        'redirects': 1,
        'lllimit': 500,
    }
    a = 1
    if a:
        categoryname = pywikibot.data.api.Request(site=site, **params).submit()
        for item in categoryname[u'query'][u'pages']:
            fanamespace = categoryname[u'query'][u'pages'][item]['ns']
        _cache[tuple([enlink, site, 'ns'])] = fanamespace
        return fanamespace
    else:
        _cache[tuple([enlink, site, 'ns'])] = False
        return False

def englishdictionry(enlink, firstsite, secondsite):
    if _cache.get(tuple([enlink, firstsite, secondsite, 'en_dic'])):
        return _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])]
    try:
        enlink = unicode(str(enlink), 'UTF-8').replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'').replace(u' ',u'_')
    except:
        enlink = enlink.replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'').replace(u' ',u'_')
    if enlink.find('#') != -1:
        _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])] = False
        return False
    if enlink == u'':
        _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])] = False
        return False
    result=link_translator(enlink,firstsite,secondsite)
    #print result
    if result:
        if result.find('#') != -1:
            _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])] = False
            return False
        _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])] = result
        return result
    else:
        _cache[tuple([enlink, firstsite, secondsite, 'en_dic'])]=False
        return False 

def link_translator(title,ensite,fasite):

    params = {
        'action': 'query',
        'redirects': '',
        'titles': title
    }
    query_res = pywikibot.data.api.Request(site=ensite, **params).submit()


    normalizeds = query_res['query'].get('normalized', [])
    if len(normalizeds):
        title = normalizeds[0]['to']
        
    redirects = query_res['query'].get('redirects', [])
    if len(redirects):
        title = redirects[0]['to']


    wikidata = pywikibot.Site('wikidata', 'wikidata')
    
    endbName = ensite.dbName()
    fadbName = fasite.dbName()
    params = {
        'action': 'wbgetentities',
        'sites': endbName,
        'titles': title,
        'props': 'sitelinks'
    }

    try:
        query_res = pywikibot.data.api.Request(site=wikidata, **params).submit()
    except:
        return ''

    matches_titles = {}
    entities = query_res.get('entities', {})
    for qid, entity in entities.items():
        if fadbName in entity.get('sitelinks', {}):
            fa_title = entity['sitelinks'][fadbName]

            # for not updated since addition of badges on Wikidata items
            if not isinstance(title, str):
                fa_title = fa_title['title']

            return fa_title

    return ''


def catquery(enlink, firstsite, hidden):
    if _cache.get(tuple([enlink, firstsite, hidden, 'cat_query'])):
        return _cache[tuple([enlink, firstsite, hidden, 'cat_query'])]
    cats = []
    try:
        enlink = unicode(str(enlink), 'UTF-8').replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    except:
        enlink = enlink.replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    enlink = enlink.split(u'#')[0].strip()
    if enlink == u'':
        _cache[tuple([enlink, firstsite, hidden, 'cat_query'])] = False
        return False
    enlink = enlink.replace(u' ', u'_')
    site = pywikibot.Site(firstsite)
    params = {
        'action': 'query',
        'prop': 'categories',
        'titles': enlink,
        'redirects': 1,
        'cllimit': 500,
    }
    if not hidden:
        params['clshow'] = '!hidden'
    try:
        categoryname = pywikibot.data.api.Request(site=site, **params).submit()
        for item in categoryname[u'query'][u'pages']:
            categoryha = categoryname[u'query'][u'pages'][item][u'categories']
            break
        for cat in categoryha:
            cats.append(cat[u'title'])
        _cache[tuple([enlink, firstsite, hidden, 'cat_query'])] = cats
        return cats
    except:
        _cache[tuple([enlink, firstsite, hidden, 'cat_query'])] = False
        return False

def templatequery(enlink, firstsite):
    if _cache.get(tuple([enlink, firstsite, 'tem_query'])):
        return _cache[tuple([enlink, firstsite, 'tem_query'])]
    temps = []
    try:
        enlink = unicode(str(enlink), 'UTF-8').replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    except:
        enlink = enlink.replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    enlink = enlink.split(u'#')[0].strip()
    if enlink == u'':
        _cache[tuple([enlink, firstsite, 'tem_query'])] = False
        return False
    enlink = enlink.replace(u' ', u'_')
    site = pywikibot.Site(firstsite)
    params = {
        'action': 'query',
        'prop': 'templates',
        'titles': enlink,
        'redirects': 1,
        'tllimit': 500,
    }

    try:
        categoryname = pywikibot.data.api.Request(site, **params).submit()
        for item in categoryname[u'query'][u'pages']:
            templateha = categoryname[u'query'][u'pages'][item][u'templates']
            break
        for temp in templateha:
            temps.append(temp[u'title'].replace(u'_', u' '))
        return temps
    except:
        _cache[tuple([enlink, firstsite, 'tem_query'])] = False
        return False

def subcatquery(enlink, firstsite):
    if _cache.get(tuple([enlink, firstsite, 'subcat_query'])):
        return _cache[tuple([enlink, firstsite, 'subcat_query'])]
    cats = []
    try:
        enlink = unicode(str(enlink), 'UTF-8').replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    except:
        enlink = enlink.replace(u'[[', u'').replace(u']]', u'').replace(u'en:', u'').replace(u'sd:', u'')
    enlink = enlink.split(u'#')[0].strip()
    if enlink == u'':
        _cache[tuple([enlink, firstsite, 'subcat_query'])] = False
        return False
    enlink = enlink.replace(u' ', u'_')
    site = pywikibot.Site(firstsite)
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': enlink,
        'cmtype': 'subcat',
        'cmlimit': 500,
    }
    try:
        categoryname = pywikibot.data.api.Request(site=site, **params).submit()
        for item in categoryname[u'query'][u'categorymembers']:
            categoryha = item[u'title']
            pywikibot.output(categoryha)
            cats.append(categoryha)
        if cats != []:
            _cache[tuple([enlink, firstsite, 'subcat_query'])] = cats
            return cats
    except:
        _cache[tuple([enlink, firstsite, 'subcat_query'])] = False
        return False

def sitop(link, wiki):
    link = link.replace(u'[[', u'').replace(u']]', u'').strip()
    site = pywikibot.Site(wiki)
    try:
        page = pywikibot.Page(site, link)
        if wiki == 'sd':
            cats = page.categories()
        else:
            cats = pywikibot.textlib.getCategoryLinks(page.get(), site=site)
        return cats
    except pywikibot.IsRedirectPage:
        return False
    except:
        return False

def category(PageTitle, koltuple):
    counters = 0
    PageTitle = PageTitle.replace(u'[[', u'').replace(u']]', u'').strip()
    listacategory = [PageTitle]
    listacategory2 = []
    for catname in listacategory:
        counters += 1
        if counters > 150:
            break
        gencat = subcatquery(catname, 'sd')  # ---function
        if not gencat:
            time.sleep(5)
            gencat = subcatquery(catname, 'sd')
        if gencat:
            if len(gencat) > 100:
                continue
            for subcat in gencat:
                subcat2 = u'[[sd:' + subcat + u']]'
                if subcat in listacategory:
                    continue
                else:
                    listacategory.append(subcat)
                    if subcat2 in koltuple:
                        listacategory2.append(subcat2)
                        listacategory2.append(' ')
                        return listacategory2
    if listacategory == []:
        return False
    else:
        return listacategory

def pagefafinder(encatTitle):

    cats = []
    try:
        item = unicode(str(encatTitle), 'Ascii').replace('[[en:', '').replace(']]', '').replace(' ', '_').replace('Category:', '')
    except:
        item = str(encatTitle).replace('[[en:', '').replace(']]', '').replace(' ', '_').replace('Category:', '')
    # -----------------start sql---------------------------------------
    queries = 'SELECT /* SLOW_OK */ ll_title,page_namespace  FROM page JOIN categorylinks JOIN langlinks WHERE cl_to = "' + item + '" AND cl_from=page_id AND page_id =ll_from AND ll_lang = "sd" GROUP BY ll_title ;'
    cn = MySQLdb.connect("enwiki.labsdb", db=en_site.dbName()+ '_p', user=config.db_username, passwd=config.db_password)
    cur = cn.cursor()
    cur.execute(queries)
    results = cur.fetchall()
    cn.close()
    # -----------------end of sql--------------------------------------------
    for raw in results:
       raw=list(raw)
       cats.append([raw[0],raw[1]])
    if cats != []:
        return cats
    else:
        return False

def duplic(catfa, radeh):
    catfa = catfa.replace(u'sd:', u'')
    radeht = u' '
    if len(radeh.strip()) < 1:
        return False
    if len(catfa.replace(u',', u'').strip()) < 1:
        return radeh
    for x in catfa.split(','):
        catfax = x.split('|')[0].split(']]')[0].replace('[[', '').strip()
        for y in radeh.split(','):
            radehy = y.split('|')[0].split(']]')[0].replace('[[', '').strip()
            if catfax == radehy:
                radeh = radeh.replace(y, '')
                break
    for rad in radeh.split(','):
        radeht += rad + '\n'
    return radeht

def pedar(catfa, radehi, link):
    link = link.replace(u'[[', u'').replace(u']]', u'').strip()
    hazflist = catfa
    if englishdictionry(link, fa_site, en_site) is False:
        return hazflist
    radehi = re.sub(ur'\n+?', ur'\n', radehi.strip())
    kol = catfa.strip() + radehi.replace('\n', ',').strip()
    kol = kol.replace(',,', ',').strip()
    radehtest = radehi.replace('\n', ',').replace(',,', ',').strip().split(',')
    koltuple = kol.split(',')
    for x in range(0, len(radehtest)):
        if radehtest[x].find(u'مضمون') != -1:
            continue
        catslistx = category(radehtest[x], koltuple)  # ----------category function
        if catslistx is False:
            continue
        for y in range(0, len(koltuple)):
            if radehi.find(radehtest[x]) == -1:
                break
            for catlis in catslistx:
                try:
                    catlis = unicode(str(catlis), 'UTF-8').strip()
                except:
                    catlis = catlis.strip()
                if koltuple[y].strip() == catlis:
                    if radehi.find(radehtest[x]) != -1:
                        hazfi = radehtest[x].replace(u'[[', u'').replace(u']]', u'').replace(
                            u'زمرو:', u'').replace(u'Category:', u'').strip()
                        try:
                            hazfi = re.search(u'\[\[ *(?:[Cc]ategory|زمرو) *:*%s*(?:\|.*?|)\]\]' % hazfi, radehi).group(0)
                            radehi = radehi.replace(hazfi, '')
                        except:
                            try:
                                radehi = radehi.replace(u'(', u' اااا ').replace(u')', u' بببب ')
                                hazfi = hazfi.replace(u'(', u' اااا ').replace(u')', u' بببب ')
                                hazfi = re.search(u'\[\[ *(?:[Cc]ategory|زمرو) *:*%s*(?:\|.*?|)\]\]' % hazfi, radehi)
                                if hazfi:
                                    hazfi= hazfi.group(0)
                                    radehi = radehi.replace(hazfi, '')
                                    radehi = radehi.replace(u' اااا ', u'(').replace(u' بببب ', u')')
                            except:
                                pass
                        radehi = radehi.replace('\n\n', '\n').strip()
                        break
    radehi = radehi.replace(',', '\n').strip()
    return radehi

def run(gen):
    for pagework in gen:
            
        try:
            radehf, catsfas, maghalehen, radeh, finallRadeh = ' ', ' ', ' ', ' ', ' '
            try:
                pagework = unicode(str(pagework), 'UTF-8')
            except:
                pagework = pagework

            if pagework in page_list_run:
                continue
            else:
                page_list_run.append(pagework)

            pywikibot.output(u'-----------------------------------------------')
            pywikibot.output(u'opening....' + pagework)
            catsfa = sitop(pagework, 'sd')
            if catsfa is False:
                continue
            for tem in catsfa:
                #if unicode(str(tem), 'UTF-8').find(u'رده:مقاله‌های ایجاد شده توسط ایجادگر') != -1:
                #    continue
                cat_queries_result=catquery(unicode(str(tem), 'UTF-8'), 'sd', True)
                if cat_queries_result:
                    if u'زمرو:پوشيدهه زمرا' in cat_queries_result:
                        pywikibot.output(u'>> Continueing the hidden category '+unicode(str(tem), 'UTF-8'))
                        continue
                catsfas += unicode(str(tem), 'UTF-8') + ','
            maghalehen = englishdictionry(pagework, fa_site, en_site)
            if not maghalehen:
                continue
            pageblacklist = [u'Sandbox']
            passing = True
            for item in pageblacklist:
                if maghalehen.find(item.lower()) != -1:
                    passing = False
                    break
            if not passing:
                continue
            if namespacefinder(maghalehen, en_site) != namespacefinder(pagework, fa_site):
                pywikibot.output(u"\03{lightred}Interwikis have'nt the same namespace\03{default}")
                continue
            catsen = catquery(maghalehen, 'en', False)
            if not catsen:
                time.sleep(5)
                catsen = catquery(maghalehen, 'en', False)
                if not catsen:
                    continue
            templateblacklist = [u'Wikipedia category', u'sockpuppet', u'Empty category', u'tracking category',
                                 u'container category', u'hiddencat', u'backlog subcategories', u'Stub category']
            nameblcklist = [u'Current events', u'Tracking', u'articles‎', u'Surnames', u'Loanword',
                            u'Words and phrases', u'Given names', u'Human names', u'stubs‎', u'Nicknames']
            for cat in catsen:
                passport = True
                temples = str(templatequery(cat, 'en')).replace(u'_', u' ').strip()
                cat = cat.replace(u'_', u' ').strip()
                if namespacefinder(pagework, fa_site) != 14:
                    for black in templateblacklist:
                        if temples.lower().find(black.lower()) != -1:
                            passport = False
                            break
                for item in nameblcklist:
                    if cat.lower().find(item.lower()) != -1:
                        passport = False
                        break
                if not passport:
                    continue
                interwikifarsibase = englishdictionry(cat, en_site, fa_site)
                if interwikifarsibase:
                    if interwikifarsibase.find(u',') != -1:
                        try:
                            errorpage = pywikibot.Page(fa_site, u'user:ZumrahBot/CategoriesWithBadNames')
                            texterror = errorpage.get()
                            if texterror.find(interwikifarsibase) == -1:
                                texterror += u'\n#[[:' + interwikifarsibase + u']]'
                                errorpage.put(texterror, u'خودکار: اطلاع غلط عنوان')
                            continue
                        except:
                            continue
                    interwikifarsi = u'[[' + interwikifarsibase + u']]'
                    if cat == englishdictionry(interwikifarsibase, fa_site, en_site):
                        radeh += interwikifarsi + u','
            radehf = duplic(catsfas, radeh)
            if radehf is False:
                continue
            radehf = radehf.replace('\n\n', '\n').replace('\n\n', '\n').replace('\n\n', '\n').replace('\n\n', '\n').strip()
            if radehf == "":
                continue
            if catsfas.strip() != u'':
                finallRadeh = pedar(catsfas, radehf, pagework)
            else:
                finallRadeh = radehf.replace(',', '\n')
            if finallRadeh is False:
                continue
            if finallRadeh.replace('\n', '').strip() == '':
                continue
            try:
                link = pagework.replace(u'[[', u'').replace(u']]', u'').strip()
                page = pywikibot.Page(fa_site, link)

                try:
                    text = page.get()
                except pywikibot.IsRedirectPage:
                    continue
                except:
                    pywikibot.output(u'\03{lightred}Could not open page\03{default}')
                    continue
                namespaceblacklist = [1, 2, 3, 5, 7, 8, 9, 11, 13, 15, 101, 103,118,119,446,447, 828, 829]
                if page.namespace() in namespaceblacklist:
                    continue
                if text.find(u'{{مساوی زمرہ نہیں}}') != -1 or text.find(u'{{الگو:رده همسنگ نه}}') != -1 or text.find(u'{{رده‌همسنگ نه}}') != -1 or text.find(u'{{واپس منتقل زمرو') != -1:
                    pywikibot.output(u'\03{lightred}this page had {{رده همسنگ نه}} so it is skipped!\03{default}')
                    continue
                #---------------------------------------remove repeative category-----------------
                text = text.replace(u']]‌', u']]@12@').replace(u'‌[[', u'@34@[[')  # for solving ZWNJ+[[ or ]]+ZWNJ Bug
                for item in finallRadeh.split(u'\n'):
                    item2 = item.split(u'|')[0].replace(u'[[', u'').replace(u']]', u'').strip()
                    radehbehtar = templatequery(item2, 'sd')
                    if radehbehtar:
                        if (u'سانچو:واپس منتقل زمرو' in radehbehtar) or (u'الگو:delete' in radehbehtar) or (u'سانچہ:فوری حذف شدگی' in radehbehtar):
                            pywikibot.output(
                                u'\03{lightred}Category %s had {{رده بهتر}} or  {{delete}} so it is skipped! please edit en.wiki interwiki\03{default}' % item2)
                            finallRadeh = finallRadeh.replace(item, u'').replace(u'\n\n', u'\n')
                            continue
                    textremove = text.replace(u'  |', u'|').replace(u' |', u'|').replace(
                        u' |', u'|').replace(u'|  ', u'|').replace(u'| ', u'|')
                    if textremove.find(u'{{رده همسنگ میلادی نه}}') != -1 or textremove.find(u'{{الگو:رده همسنگ میلادی نه}}') != -1:
                        if item.find(u'(عیسوی)') != -1 or item.find(u'(ق م)') != -1 or item.find(u'(قبل مسیح)') != -1:
                            finallRadeh = finallRadeh.replace(item, u'').replace(u'\n\n', u'\n')
                    if textremove.find(u'زمرو:فوت ٿيل شخصيتون') != -1:
                        if item.find(u'بقید حیات شخصیات') != -1 or item.find(u'بقید_حیات_شخصیات') != -1:
                            finallRadeh = finallRadeh.replace(item, u'').replace(u'\n\n', u'\n')
                    if item.find(u'فوری_حذف_شدگی') != -1 or item.find(u'فوری حذف شدگی') != -1:
                        finallRadeh = finallRadeh.replace(item, u'').replace(u'\n\n', u'\n')
                    if textremove.find(item2 + u']]') != -1 or textremove.find(item2 + u'|') != -1:
                        finallRadeh = finallRadeh.replace(item, u'').replace(u'\n\n', u'\n')

                if finallRadeh.replace(u'\r', u'').replace(u'\n', u'').strip() == u'':
                    continue
                finallRadeh = finallRadeh.replace(u'\r', u'').replace(u'\n\n\n\n', u'\n').replace(u'\n\n\n', u'\n').replace(u'\n\n', u'\n').replace(u'\n\n', u'\n').replace(
                    u'\n\n', u'\n').replace(u'\n\n', u'\n').replace(u'\n\n', u'\n').replace(u'\n\n', u'\n')  # ---------------------------------------------------------------------------------
                if text.find(ur'زمرو:') != -1 and page.namespace() != 10:
                    num = text.find(u'[[زمرو:')
                    text = text[:num] + finallRadeh + '\n' + text[num:]
                else:
                    m = re.search(ur'\[\[([a-z]{2,3}|[a-z]{2,3}\-[a-z\-]{2,}|simple):.*?\]\]', text)
                    if m:
                        if m.group(0) == u'[[en:Article]]':
                            try:
                                if string.count(text, u'[[en:Article]] --->') == 1:
                                    finallRadeh = re.sub(ur'\n+?', '\n', finallRadeh.replace('\r', '')).strip()
                                    text = text.split(u'[[en:Article]] --->')[0] + \
                                        u'[[en:Article]] --->\n' + finallRadeh + \
                                        text.split(u'[[en:Article]] --->')[1]
                                else:
                                    if page.namespace() == 10:
                                        continue
                                    text += '\n' + finallRadeh
                            except:
                                if page.namespace() == 10:
                                    continue
                                text += '\n' + finallRadeh
                        else:
                            num = text.find(m.group(0))
                            text = text[:num] + finallRadeh + '\n' + text[num:]
                    else:
                        if page.namespace() == 10:
                            continue
                        text += '\n' + finallRadeh
                pywikibot.output(u'\03{lightpurple} Added==' + finallRadeh + u"\03{default}")
                radehfmsg = finallRadeh.strip().replace(u'\n', u'+')
                if len(radehfmsg.split(u'+')) > 4:
                    numadd = str(len(radehfmsg.split(u'+'))).replace(u'0', u'0').replace(u'1', u'1').replace(u'2', u'2').replace(u'3', u'3').replace(
                        u'4', u'4').replace(u'5', u'5').replace(u'6', u'6').replace(u'7', u'7').replace(u'8', u'8').replace(u'9', u'9')
                    radehfmsg = u' %s زمرو' % numadd
                msg = u'خودکار: اضافہ زمرہ جات %s: + %s'
                text_new = text
                if page.namespace() == 0:  # ----------------cleaning
                    text_new, cleaning_version, msg_clean = fa_cosmetic_changes_core.fa_cosmetic_changes(text, page)
                else:
                    msg_clean = u' '
                msg = msg % (msg_clean, radehfmsg)
                msg = msg.replace(u'  ', u' ').strip()
                text_new = text_new.replace(u']]@12@', u']]‌').replace(u'@34@[[', u'‌[[')
                page.put(text_new.strip(), msg)

                pywikibot.output(u'\03{lightpurple} Done=' + pagework + u"\03{default}")
            except Exception as e:
                 pywikibot.output(u'\03{lightred}Could not open page\03{default}')
                 continue
        except:
            pywikibot.output(u'\03{lightred}Bot has error\03{default}')
            continue
# -------------------------------encat part-----------------------------------

def categorydown(listacategory):
    listacategory = [listacategory]
    count = 1
    for catname in listacategory:
        count += 1
        if count == 200:
            break
        gencat = pagegenerators.SubCategoriesPageGenerator(catname, recurse=False)
        for subcat in gencat:
            try:
                pywikibot.output(str(subcat))
            except:
                pywikibot.output(subcat)
            if subcat in listacategory:
                continue
            else:
                listacategory.append(subcat)
        break
    return listacategory

def encatlist(encat):
    count = 0
    listenpageTitle = []
    encat = encat.replace(u'[[', u'').replace(u']]', u'').replace(u'Category:', u'').replace(u'category:', u'').strip()
    language = 'en'
    encat = pywikibot.Category(pywikibot.Site(language), encat)
    listacategory = [encat]
    for enpageTitle in listacategory:
        try:
            fapages = pagefafinder(enpageTitle)
            if fapages is not False:
                for pages,profix_fa in fapages:
                    if  profix_fa=='14':
                        pages = u'Category:'+unicode(pages, 'UTF-8')
                    elif  profix_fa=='12':
                        pages = u'Help:'+unicode(pages, 'UTF-8')
                    elif  profix_fa=='10':
                        pages = u'Template:'+unicode(pages, 'UTF-8')
                    elif  profix_fa=='6':
                        pages = u'File:'+unicode(pages, 'UTF-8')
                    elif  profix_fa=='4':
                        pages = u'Wikipedia:'+unicode(pages, 'UTF-8')
                    elif  profix_fa=='100':
                        pages = u'Portal:'+unicode(pages, 'UTF-8')
                    elif profix_fa in ['1', '2', '3', '5', '7', '8', '9', '11', '13', '15', '101', '103','118','119','446','447', '828', '829']:
                        continue
                    else:
                        pages = unicode(pages, 'UTF-8')
                    pywikibot.output(u'\03{lightgreen}Adding ' + pages + u' to fapage lists\03{default}')
                    listenpageTitle.append(pages)

        except:

            try:
                enpageTitle = unicode(str(enpageTitle), 'UTF-8').split(u'|')[0].split(u']]')[0].replace(u'[[', u'').strip()
            except:
                enpageTitle = enpageTitle.split(u'|')[0].split(u']]')[0].replace(u'[[', u'').strip()
            cat = pywikibot.Category(pywikibot.Site(language), enpageTitle)
            gent = pagegenerators.CategorizedPageGenerator(cat)
            for pagework in gent:
                count += 1
                try:
                    link = str(pagework).split(u'|')[0].split(u']]')[0].replace(u'[[', u'').strip()
                except:
                    pagework = unicode(str(pagework), 'UTF-8')
                    link = pagework.split(u'|')[0].split(u']]')[0].replace(u'[[', u'').strip()
                pywikibot.output(link)
                fapagetitle = englishdictionry(link, en_site, fa_site)
                if fapagetitle is False:
                    continue
                else:
                    pywikibot.output(u'\03{lightgreen}Adding ' + fapagetitle + u' to fapage lists\03{default}')
                    listenpageTitle.append(fapagetitle)

    if listenpageTitle == []:
        return False, False
    return listenpageTitle, listacategory
#-------------------------------------------------------------------encat part finish--------------------------

def main():
    summary_commandline, gen, template = None, None, None
    namespaces, PageTitles, exceptions = [], [], []
    encat, newcatfile = '', ''
    autoText, autoTitle = False, False
    recentcat, newcat = False, False
    genFactory = pagegenerators.GeneratorFactory()
    for arg in pywikibot.handleArgs():
        if arg == '-autotitle':
            autoTitle = True
        elif arg == '-autotext':
            autoText = True
        elif arg.startswith('-page'):
            if len(arg) == 5:
                PageTitles.append(pywikibot.input(u'Which page do you want to chage?'))
            else:
                PageTitles.append(arg[6:])
            break
        elif arg.startswith('-except:'):
            exceptions.append(arg[8:])
        elif arg.startswith('-template:'):
            template = arg[10:]
        elif arg.startswith('-facat:'):
            facat = arg.replace(u'Category:', u'').replace(u'category:', u'').replace(u'زمرو:', u'')
            encat = englishdictionry(u'زمرو:' + facat[7:], fa_site, en_site).replace(u'Category:', u'').replace(u'category:', u'')
            break
        elif arg.startswith('-encat:'):
            encat = arg[7:].replace(u'Category:', u'').replace(u'category:', u'').replace(u'زمرو:', u'')
            break
        elif arg.startswith('-newcatfile:'):
            newcatfile = arg[12:]
            break
        elif arg.startswith('-recentcat'):
            arg = arg.replace(':', '')
            if len(arg) == 10:
                genfa = pagegenerators.RecentchangesPageGenerator()
            else:
                genfa = pagegenerators.RecentchangesPageGenerator(number=int(arg[10:]))
            genfa = pagegenerators.DuplicateFilterPageGenerator(genfa)
            genfa = pagegenerators.NamespaceFilterPageGenerator(genfa, [14])
            preloadingGen = pagegenerators.PreloadingGenerator(genfa, 60)
            recentcat = True
            break
        elif arg.startswith('-newcat'):
            arg = arg.replace(':', '')
            if len(arg) == 7:
                genfa = pagegenerators.NewpagesPageGenerator(step=100, namespaces=14)
            else:
                genfa = pagegenerators.NewpagesPageGenerator(step=int(arg[7:]), namespaces=14)
            preloadingGen = pagegenerators.PreloadingGenerator(genfa, 60)
            newcat = True
            break
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))
        elif arg.startswith('-summary:'):
            pywikibot.setAction(arg[9:])
            summary_commandline = True
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = genFactory.getCombinedGenerator(gen)
    if encat != '':
        encatfalist, encatlists = encatlist(encat)
        if encatlists:
            for encat in encatlists:
                encat = englishdictionry(encat, en_site, fa_site)
                if encat:
                    run([encat])
        if encatfalist is not False:
            run(encatfalist)
    if PageTitles:
        pages = [pywikibot.Page(fa_site, PageTitle) for PageTitle in PageTitles]
        gen = iter(pages)
    if recentcat:
        for workpage in preloadingGen:
            workpage = workpage.title()
            cat = pywikibot.Category(fa_site, workpage)
            gent = pagegenerators.CategorizedPageGenerator(cat)
            run(gent)
        pywikibot.stopme()
        sys.exit()
    if newcat:
        for workpage in preloadingGen:
            workpage = workpage.title()
            workpage = englishdictionry(workpage, fa_site, en_site)
            if workpage is not False:
                encatfalist, encatlists = encatlist(workpage)
                if encatlists:
                    for encat in encatlists:
                        encat = englishdictionry(encat, en_site, fa_site)
                        if encat:
                            run([encat])
                if encatfalist is not False:
                    run(encatfalist)
        pywikibot.stopme()
        sys.exit()
    if newcatfile:
        text2 = codecs.open(newcatfile, 'r', 'utf8')
        text = text2.read()
        linken = re.findall(ur'\[\[.*?\]\]', text, re.S)
        if linken:
            for workpage in linken:
                pywikibot.output(u'\03{lightblue}Working on --- Link ' + workpage + u' at th newcatfile\03{default}')
                workpage = workpage.split(u'|')[0].replace(u'[[', u'').replace(u']]', u'').strip()
                workpage = englishdictionry(workpage, fa_site, en_site)
                if workpage is not False:
                    encatfalist,encatlists=encatlist(workpage)
                    workpage=englishdictionry(workpage,fa_site,en_site)
                    if encatlists:
                        run(encatlists)
                    if encatfalist is not False:
                        run(encatfalist)
        pywikibot.stopme()
        sys.exit()
    if not gen:
        pywikibot.stopme()
        sys.exit()
    if namespaces != []:
        gen = pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber=60)
    run(preloadingGen)


if __name__ == '__main__':
    main()
