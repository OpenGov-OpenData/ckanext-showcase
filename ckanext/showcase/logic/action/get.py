import sqlalchemy

import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.lib.navl.dictization_functions import validate
from ckan.logic import NotAuthorized

from ckanext.showcase.logic.schema import (showcase_package_list_schema,
                                           package_showcase_list_schema)
from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseAdmin

import logging
log = logging.getLogger(__name__)

_select = sqlalchemy.sql.select
_and_ = sqlalchemy.and_


@toolkit.side_effect_free
def showcase_show(context, data_dict):
    '''Return the pkg_dict for a showcase (package).

    :param id: the id or name of the showcase
    :type id: string
    '''

    toolkit.check_access('ckanext_showcase_show', context, data_dict)

    pkg_dict = toolkit.get_action('package_show')(context, data_dict)

    return pkg_dict


@toolkit.side_effect_free
def showcase_list(context, data_dict):
    '''Return a list of all showcases in the site.'''

    toolkit.check_access('ckanext_showcase_list', context, data_dict)

    model = context["model"]

    q = model.Session.query(model.Package) \
        .filter(model.Package.type == 'showcase') \
        .filter(model.Package.state == 'active')

    showcase_list = []

    for pkg in q.all():
        pkg_dict = model_dictize.package_dictize(pkg, context)

        image_url = next((item.get('value') for item in pkg_dict.get('extras') if item.get('key') == 'image_url'), None)
        if image_url and not image_url.startswith('http'):
            pkg_dict['image_display_url'] = h.url_for_static('uploads/showcase/{0}'.format(image_url), qualified=True)

        if pkg_dict['private']:
            try:
                user = context.get('user', '')
                userobj = model.User.get(user)
                if not ShowcaseAdmin.is_user_showcase_admin(userobj):
                    showcase_list.append(pkg_dict)
            except:
                pass
        else:
            showcase_list.append(pkg_dict)
    return showcase_list


@toolkit.side_effect_free
def showcase_package_list(context, data_dict):
    '''List packages associated with a showcase.

    :param showcase_id: id or name of the showcase
    :type showcase_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_showcase_package_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           showcase_package_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of package ids associated with showcase id
    pkg_id_list = ShowcasePackageAssociation.get_package_ids_for_showcase(
        validated_data_dict['showcase_id'])

    pkg_list = []
    if pkg_id_list is not None:
        # for each package id, get the package dict and append to list if
        # active
        for pkg_id in pkg_id_list:
            try:
                pkg = toolkit.get_action('package_show')(context,
                                                         {'id': pkg_id})
                if pkg['state'] == 'active':
                    pkg_list.append(pkg)
            except NotAuthorized:
                log.debug(
                    'Not authorized to access Package with ID: ' + str(pkg_id))
    return pkg_list


@toolkit.side_effect_free
def package_showcase_list(context, data_dict):
    '''List showcases associated with a package.

    :param package_id: id or name of the package
    :type package_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_package_showcase_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           package_showcase_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of showcase ids associated with the package id
    showcase_id_list = ShowcasePackageAssociation.get_showcase_ids_for_package(
        validated_data_dict['package_id'])

    showcase_list = []
    if showcase_id_list is not None:
        for showcase_id in showcase_id_list:
            showcase = toolkit.get_action('package_show')(context,
                                                          {'id': showcase_id})
            showcase_list.append(showcase)

    return showcase_list


@toolkit.side_effect_free
def showcase_admin_list(context, data_dict):
    '''
    Return a list of dicts containing the id and name of all active showcase
    admin users.

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_showcase_admin_list', context, data_dict)

    model = context["model"]

    user_ids = ShowcaseAdmin.get_showcase_admin_ids()

    if user_ids:
        q = model.Session.query(model.User) \
            .filter(model.User.state == 'active') \
            .filter(model.User.id.in_(user_ids))

        showcase_admin_list = []
        for user in q.all():
            showcase_admin_list.append({'name': user.name, 'id': user.id})
        return showcase_admin_list

    return []
