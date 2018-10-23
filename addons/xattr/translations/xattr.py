from addons.xattr.i18n import en, ja
from .project_attribute import _project_attribute_translations
from .funding_attribute import _funding_attribute_translations
from .contributor_attribute import _contributor_attribute_translations


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

    _xattr_translations(translations, gettext)
    _project_attribute_translations(translations, gettext)
    _funding_attribute_translations(translations, gettext)
    _contributor_attribute_translations(translations, gettext)

    # Decode to utf-8 to make Japanese work properly
    for key in translations:
        translations[key] = translations[key].decode('utf-8')

    return translations


def _xattr_translations(t, _):
    t['Attributes'] = _('Attributes')
    t['Base'] = _('Base')
    t['Fundings'] = _('Fundings')
    t['Contributors'] = _('Contributors')
    t['Save'] = _('Save')
    t['Cancel'] = _('Cancel')
    t['Remove'] = _('Remove')
    t['Add'] = _('Add')
    t['Edit'] = _('Edit')
    t['Start Date'] = _('Start Date')
    t['End Date'] = _('End Date')
    t['Start'] = _('Start')
    t['Complete'] = _('Complete')
    t['Close'] = _('Close')
    t['Save Changes'] = _('Save Changes')
