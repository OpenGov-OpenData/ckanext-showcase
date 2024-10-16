# -*- coding: utf-8 -*-
import ckan.plugins.toolkit as toolkit

from ckan.logic.schema import (default_tags_schema,
                               default_extras_schema,
                               default_resource_schema)

from ckanext.showcase.logic.validators import (
    convert_package_name_or_id_to_id_for_type_dataset,
    convert_package_name_or_id_to_id_for_type_showcase,
    convert_organization_name_or_id_to_id)

if toolkit.check_ckan_version("2.10"):
    unicode_safe = toolkit.get_validator("unicode_safe")
else:
    import six
    unicode_safe = six.text_type


not_empty = toolkit.get_validator("not_empty")
empty = toolkit.get_validator("empty")
if_empty_same_as = toolkit.get_validator("if_empty_same_as")
ignore_missing = toolkit.get_validator("ignore_missing")
ignore = toolkit.get_validator("ignore")
keep_extras = toolkit.get_validator("keep_extras")

package_id_not_changed = toolkit.get_validator("package_id_not_changed")
name_validator = toolkit.get_validator("name_validator")
user_id_or_name_exists = toolkit.get_validator("user_id_or_name_exists")
package_name_validator = toolkit.get_validator("package_name_validator")
tag_string_convert = toolkit.get_validator("tag_string_convert")
ignore_not_package_admin = toolkit.get_validator("ignore_not_package_admin")
url_validator = toolkit.get_validator("url_validator")

def showcase_base_schema():
    schema = {
        'id': [empty],
        'revision_id': [ignore],
        'name': [not_empty, name_validator, package_name_validator],
        'title': [if_empty_same_as("name"), unicode_safe],
        'author': [ignore_missing, unicode_safe],
        'author_email': [ignore_missing, unicode_safe],
        'notes': [ignore_missing, unicode_safe],
        'url': [ignore_missing, url_validator],
        'state': [ignore_not_package_admin, ignore_missing],
        'type': [ignore_missing, unicode_safe],
        '__extras': [ignore],
        '__junk': [empty],
        'resources': default_resource_schema(),
        'tags': default_tags_schema(),
        'tag_string': [ignore_missing, tag_string_convert],
        'extras': default_extras_schema(),
        'save': [ignore],
        'return_to': [ignore],
        'image_url': [toolkit.get_validator('ignore_missing'),
                      toolkit.get_converter('convert_to_extras')],
        'redirect_link': [
            toolkit.get_validator('ignore_missing'),
            toolkit.get_converter('convert_to_extras')
        ]
    }
    return schema


def showcase_create_schema():
    return showcase_base_schema()


def showcase_update_schema():
    schema = showcase_base_schema()

    # Users can (optionally) supply the package id when updating a package, but
    # only to identify the package to be updated, they cannot change the id.
    schema['id'] = [ignore_missing, package_id_not_changed]

    # Supplying the package name when updating a package is optional (you can
    # supply the id to identify the package instead).
    schema['name'] = [ignore_missing, name_validator,
                      package_name_validator, unicode_safe]

    # Supplying the package title when updating a package is optional, if it's
    # not supplied the title will not be changed.
    schema['title'] = [ignore_missing, unicode_safe]

    return schema


def showcase_show_schema():
    schema = showcase_base_schema()
    # Don't strip ids from package dicts when validating them.
    schema['id'] = []

    schema.update({
        'tags': {'__extras': [keep_extras]}})

    schema.update({
        'state': [ignore_missing],
        })

    # Remove validators for several keys from the schema so validation doesn't
    # strip the keys from the package dicts if the values are 'missing' (i.e.
    # None).
    schema['author'] = []
    schema['author_email'] = []
    schema['notes'] = []
    schema['url'] = []

    # Add several keys that are missing from default_create_package_schema(),
    # so validation doesn't strip the keys from the package dicts.
    schema['metadata_created'] = []
    schema['metadata_modified'] = []
    schema['creator_user_id'] = []
    schema['num_tags'] = []
    schema['revision_id'] = [ignore_missing]
    schema['tracking_summary'] = [ignore_missing]

    schema.update({
        'image_url': [toolkit.get_converter('convert_from_extras'),
                      toolkit.get_validator('ignore_missing')],
        'original_related_item_id': [
            toolkit.get_converter('convert_from_extras'),
            toolkit.get_validator('ignore_missing')],
        'redirect_link': [
            toolkit.get_converter('convert_from_extras'),
            toolkit.get_validator('ignore_missing')]
    })

    return schema


def showcase_package_association_create_schema():
    schema = {
        'package_id': [not_empty, unicode_safe,
                       convert_package_name_or_id_to_id_for_type_dataset],
        'showcase_id': [not_empty, unicode_safe,
                        convert_package_name_or_id_to_id_for_type_showcase],
        'organization_id': [ignore_missing, unicode_safe,
                            convert_organization_name_or_id_to_id]
    }
    return schema


def showcase_package_association_delete_schema():
    return showcase_package_association_create_schema()


def showcase_package_list_schema():
    schema = {
        'showcase_id': [not_empty, unicode_safe,
                        convert_package_name_or_id_to_id_for_type_showcase]
    }
    return schema


def package_showcase_list_schema():
    schema = {
        'package_id': [not_empty, unicode_safe,
                       convert_package_name_or_id_to_id_for_type_dataset]
    }
    return schema


def organization_showcase_list_schema():
    schema = {
        'organization_id': [not_empty, unicode_safe,
                            convert_organization_name_or_id_to_id]
    }
    return schema


def showcase_admin_add_schema():
    schema = {
        'username': [not_empty, user_id_or_name_exists, unicode_safe],
    }
    return schema


def showcase_admin_remove_schema():
    return showcase_admin_add_schema()
