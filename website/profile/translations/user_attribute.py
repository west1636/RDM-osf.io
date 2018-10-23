# coding:utf-8
from website.profile.i18n import en, ja


def translate(lang_list):
    if not isinstance(lang_list, list):
        raise TypeError

    t = {}
    for lang in lang_list:
        if lang == 'en':
            en.install()
            t[lang] = _generate_translations(en.gettext)

        elif lang == 'ja':
            ja.install()
            t[lang] = _generate_translations(ja.gettext)

    return t


def _generate_translations(gettext):
    translations = {}

    _user_attribute_translations(translations, gettext)

    # Decode to utf-8 to make Japanese work properly
    for key in translations:
        translations[key] = translations[key].decode('utf-8')

    return translations


def _user_attribute_translations(t, _):
    t['User Extended Information Edit'] = _('User Extended Information Edit')
    t[u'Full Name (e.g. Yamada Taro)'] = _('Full Name (e.g. Yamada Taro)')
    t[u'Given Name (e.g. Taro)'] = _('Given Name (e.g. Taro)')
    t['Middle Name'] = _('Middle Name')
    t[u'Family Name (e.g. Yamada)'] = _('Family Name (e.g. Yamada)')
    t['Suffix'] = _('Suffix')
    t['Alias'] = _('Alias')
    t['Full Name(kana)'] = _('Full Name(kana)')
    t['Given Name(kana)'] = _('Given Name(kana)')
    t['Middle Name(kana)'] = _('Middle Name(kana)')
    t['Family Name(kana)'] = _('Family Name(kana)')
    t['Suffix(kana)'] = _('Suffix(kana)')
    t['Alias(kana)'] = _('Alias(kana)')
    t['E-Rad ID'] = _('E-Rad ID')
    t['ResearchMap ID'] = _('ResearchMap ID')
    t['Organization Type'] = _('Organization Type')
    t['Idp'] = _('Idp')
    t['Idp Organization Name'] = _('Idp Organization Name')
    t['Idp Organization Habitation'] = _('Idp Organization Habitation')
    t['Idp Organization Phone Number'] = _('Idp Organization Phone Number')
    t['Idp Organization Address'] = _('Idp Organization Address')
    t['Idp Organization Icon'] = _('Idp Organization Icon')
    t['Idp Organization Banner'] = _('Idp Organization Banner')
    t['Organization'] = _('Organization')
    t['Organization Stratum Relations'] = _('Organization Stratum Relations')
    t['Organization Department Name'] = _('Organization Department Name')
    t['Organization Country'] = _('Organization Country')
    t['Organization Code'] = _('Organization Code')
    t['Organization Habitation'] = _('Organization Habitation')
    t['Organization Web URL'] = _('Organization Web URL')
    t['Degree'] = _('Degree')
    t['Start Date'] = _('Start Date')
    t['End Date'] = _('End Date')
