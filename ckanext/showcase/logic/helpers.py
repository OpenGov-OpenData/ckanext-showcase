import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.showcase.controller:ShowcaseController',
        action='search')


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': 'dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats


def get_recent_showcase_list(num=24):
    """Return a list of recent showcases."""
    showcases = []
    showcases = tk.get_action('ckanext_showcase_list')({},{})
    sorted_showcases = sorted(showcases, key=lambda k: k['metadata_modified'], reverse=True)

    return sorted_showcases[:num]


def get_package_showcase_list(package_id):
    showcases = []
    try:
        showcases = tk.get_action('ckanext_package_showcase_list')({},{'package_id':package_id})
    except:
        return []
    return showcases

def get_value_from_showcase_extras(extras, key):
    value = ''
    for item in extras:
        if item.get('key') == key:
            value = item.get('value')
    return value
