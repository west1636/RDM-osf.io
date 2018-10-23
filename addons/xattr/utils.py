import requests
from website import settings


def serialize_xattr_widget(node):
    node_addon = node.get_addon('xattr')
    pid = node._id
    project = requests.get('%sv2/attributes/project?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    ))
    fundings = requests.get('%sv2/attributes/funding?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    ))
    contributors = requests.get('%sv2/attributes/contributor?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    ))
    xattr_widget_data = {
        'complete': True,
        'more': True,
        'project': project.text,
        'fundings': fundings.text,
        'contributors': contributors.text
    }
    xattr_widget_data.update(node_addon.config.to_json())
    return xattr_widget_data
