# flake8: noqa: E128
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-24 12:20
from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


def create_groups_and_permissions(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    emit_post_migrate_signal(2, False, db_alias)

    Group = apps.get_model('auth.Group')
    Permission = apps.get_model('auth.Permission')
    GroupPagePermission = apps.get_model('wagtailcore.GroupPagePermission')
    BannerIndexPage = apps.get_model('core.BannerIndexPage')
    SectionIndexPage = apps.get_model('core.SectionIndexPage')
    FooterIndexPage = apps.get_model('core.FooterIndexPage')
    PollsIndexPage = apps.get_model('polls.PollsIndexPage')
    SurveysIndexPage = apps.get_model('surveys.SurveysIndexPage')
    YourWordsCompetitionIndexPage = apps.get_model(
        'yourwords.YourWordsCompetitionIndexPage')

    # remove the existing groups
    Group.objects.all().delete()

    # **** Get IndexPages ****
    sections = SectionIndexPage.objects.all()
    banners = BannerIndexPage.objects.all()
    footers = FooterIndexPage.objects.all()
    polls = PollsIndexPage.objects.all()
    surveys = SurveysIndexPage.objects.all()
    yourwords = YourWordsCompetitionIndexPage.objects.all()

    # **** Get Permission ****

    # Wagtail
    access_admin = get_permission(Permission, 'access_admin')

    # Comment
    add_cannedresponse = get_permission(Permission, 'add_cannedresponse')
    change_cannedresponse = get_permission(Permission, 'change_cannedresponse')
    delete_cannedresponse = get_permission(Permission, 'delete_cannedresponse')
    add_molocomment = get_permission(Permission, 'add_molocomment')
    change_molocomment = get_permission(Permission, 'change_molocomment')
    delete_molocomment = get_permission(Permission, 'delete_molocomment')
    add_comment = get_permission(Permission, 'add_comment')
    change_comment = get_permission(Permission, 'change_comment')
    delete_comment = get_permission(Permission, 'delete_comment')
    can_moderate = get_permission(Permission, 'can_moderate')

    # Surveys
    add_segmentusergroup = get_permission(
        Permission, 'add_segmentusergroup')
    change_segmentusergroup = get_permission(
        Permission, 'change_segmentusergroup')
    delete_segmentusergroup = get_permission(
        Permission, 'delete_segmentusergroup')
    add_segment = get_permission(Permission, 'add_segment')
    change_segment = get_permission(Permission, 'change_segment')
    delete_segment = get_permission(Permission, 'delete_segment')

    # Your Words
    add_yourwords_entries = get_permission(
        Permission, 'add_yourwordscompetitionentry')
    change_yourwords_entries = get_permission(
        Permission, 'change_yourwordscompetitionentry')
    delete_yourwords_entries = get_permission(
        Permission, 'delete_yourwordscompetitionentry')

    # User Profile
    change_userprofile_settings = get_permission(
        Permission, 'change_userprofilessettings')

    # Wagtail Page permission
    page_permission_types = ('add', 'edit', 'publish', 'bulk_delete', 'lock')

    # **** Create wagtail groups ****

    # <----- Product Admin ----->
    product_admin_group = create_group(Group, 'Product Admin')
    # Page permissions
    create_page_permission(GroupPagePermission, product_admin_group, sections, page_permission_types)
    create_page_permission(GroupPagePermission, product_admin_group, banners, page_permission_types)
    create_page_permission(GroupPagePermission, product_admin_group, footers, page_permission_types)
    create_page_permission(GroupPagePermission, product_admin_group, yourwords, page_permission_types)
    create_page_permission(GroupPagePermission, product_admin_group, polls, page_permission_types)
    create_page_permission(GroupPagePermission, product_admin_group, surveys, page_permission_types)
    # Django permissions
    product_admin_group.permissions.add(
        access_admin, add_yourwords_entries, change_yourwords_entries,
        delete_yourwords_entries, add_molocomment)

    # <----- Data Admin ----->
    data_admin_group = create_group(Group, 'Data Admin')
    # Page permissions
    create_page_permission(GroupPagePermission, data_admin_group, polls, page_permission_types)
    create_page_permission(GroupPagePermission, data_admin_group, surveys, page_permission_types)
    # Django permissions
    data_admin_group.permissions.add(
        access_admin, add_yourwords_entries, add_segment,
        change_segment, delete_segment, add_segmentusergroup,
        change_segmentusergroup, delete_segmentusergroup, add_molocomment)

    # <----- Data Viewer ----->
    data_viewer_group = create_group(Group, 'Data Viewer')
    # Django permissions
    data_viewer_group.permissions.add(access_admin, add_yourwords_entries, add_molocomment)

    # <----- Content Admin ----->
    content_admin_group = create_group(Group, 'Content Admin')
    # Page permissions
    create_page_permission(GroupPagePermission, content_admin_group, sections, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, banners, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, footers, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, yourwords, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, polls, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, surveys, page_permission_types)
    # Django permissions
    content_admin_group.permissions.add(
        access_admin, add_cannedresponse, change_cannedresponse,
        delete_cannedresponse, add_molocomment, change_molocomment,
        delete_molocomment, add_comment, change_comment, delete_comment,
        add_yourwords_entries, change_yourwords_entries,
        delete_yourwords_entries, change_userprofile_settings, add_segment,
        change_segment, delete_segment, add_segmentusergroup,
        change_segmentusergroup, delete_segmentusergroup)

    # <----- Content Editor ----->
    content_editor_group = create_group(Group, 'Content Editor')
    # Page permissions
    create_page_permission(GroupPagePermission, content_editor_group, sections, page_permission_types)
    create_page_permission(GroupPagePermission, content_editor_group, banners, page_permission_types)
    create_page_permission(GroupPagePermission, content_editor_group, footers, page_permission_types)
    create_page_permission(GroupPagePermission, content_editor_group, yourwords, page_permission_types)
    create_page_permission(GroupPagePermission, content_editor_group, polls, page_permission_types)
    create_page_permission(GroupPagePermission, content_admin_group, surveys, page_permission_types)
    # Django permissions
    content_editor_group.permissions.add(
        access_admin, add_cannedresponse, change_cannedresponse,
        delete_cannedresponse, add_comment, change_comment, delete_comment,
        add_yourwords_entries, change_yourwords_entries,
        delete_yourwords_entries, change_userprofile_settings)

    # <----- Comment Moderator ----->
    comment_moderator_group = create_group(Group, 'Comment Moderator')
    # Django permissions
    comment_moderator_group.permissions.add(
        access_admin, add_cannedresponse, change_cannedresponse,
        delete_cannedresponse, add_molocomment, change_molocomment,
        delete_molocomment, add_comment, change_comment, delete_comment,
        can_moderate)


def create_group(Group, group_name):
    group, _created = Group.objects.get_or_create(name=group_name)
    return group


def get_permission(Permission, code_name):
    return Permission.objects.get(codename=code_name)


def create_page_permission(GroupPagePermission, group, pages, page_permission_type):
    for page in pages:
        for permission_type in page_permission_type:
            GroupPagePermission.objects.get_or_create(
                group=group, page=page, permission_type=permission_type)


class Migration(migrations.Migration):
    dependencies = [
        ('gem', '0029_remove_extra_params'),
        ('core', '0077_molo_page'),
        ('profiles', '0021_remove_uuid_null'),
        ('polls', '0004_add-polls-permissions-to-groups'),
        ('yourwords', '0007_add_yourwords_permission_to_groups'),
        ('surveys', '0026_remove_molosurveypageview_tag'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('wagtailadmin', '0001_create_admin_access_permissions'),
        ('wagtailusers', '0005_make_related_name_wagtail_specific'),
        ('sites', '0002_alter_domain_unique'),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions),
    ]
