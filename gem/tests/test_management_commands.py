# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from os.path import join

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO

from wagtail.images.tests.utils import Image, get_test_image_file

from molo.core.models import (
    SiteLanguageRelation, Languages,
    ArticlePage, BannerPage, SectionIndexPage,
    BannerIndexPage, Tag, SectionPage)

from molo.commenting.models import MoloComment

from gem.tests.base import GemTestCaseMixin


class GemManagementCommandsTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.language_setting = Languages.objects.get(
            site_id=self.main.get_site().pk)
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')

        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')

        self.content_type = ContentType.objects.get_for_model(self.user)
        Image.objects.create(
            title="Yes.png",
            file=get_test_image_file(),
        )
        Image.objects.create(
            title="No.png",
            file=get_test_image_file(),
        )
        Image.objects.create(
            title="Maybe.png",
            file=get_test_image_file(),
        )

    def test_create_new_banner_relations(self):
        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main2).first(), title='Your mind')
        first_main_article = self.mk_article(
            parent=self.yourmind, title='first_main_article')
        first_main_banner = BannerPage(
            title='first_main_banner', slug='firstmainbanner',
            banner_link_page=first_main_article)
        self.banner_index = BannerIndexPage.objects.child_of(
            self.main).first()
        self.banner_index.add_child(instance=first_main_banner)
        first_main_banner.save_revision().publish()
        second_main_article = self.mk_article(
            parent=self.yourmind2, title='first_main_article')
        second_main_article.slug = first_main_article.slug
        second_main_article.save_revision().publish()
        second_main_banner = BannerPage(
            title='second_main_banner', slug='secondmainbanner',
            banner_link_page=first_main_article)
        self.banner_index2 = BannerIndexPage.objects.child_of(
            self.main2).first()
        self.banner_index2.add_child(instance=second_main_banner)
        second_main_banner.save_revision().publish()

        out = StringIO()
        call_command('create_new_banner_link_page_relations', stdout=out)
        second_main_banner = BannerPage.objects.get(pk=second_main_banner.pk)
        self.assertEqual(
            second_main_banner.banner_link_page.pk, second_main_article.pk)

    def test_convert_title_to_sentence_case(self):
        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind')
        spanish_capitals_spaced_article = self.mk_article(
            parent=self.yourmind, title=' ¿QUE TAL?')
        spaced_article = self.mk_article(
            parent=self.yourmind, title='  spaced article title')
        spaced_article.unpublish()
        self.assertFalse(spaced_article.live)
        russian_capitals_article = self.mk_article(
            parent=self.yourmind, title='Ё Ф')
        out = StringIO()
        call_command('format_titles_sentence_case', stdout=out)
        new_spanish_article = ArticlePage.objects.get(
            pk=spanish_capitals_spaced_article.pk)
        new_spaced_article = ArticlePage.objects.get(
            pk=spaced_article.pk)
        new_russian_article = ArticlePage.objects.get(
            pk=russian_capitals_article.pk)
        self.assertEqual(new_spanish_article.title, u'¿Que tal?')
        self.assertEqual(new_spaced_article.title, u'spaced article title')
        self.assertFalse(spaced_article.live)
        self.assertEqual(new_russian_article.title, u'Ё ф')

    def test_add_images_to_articles(self):
        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Main language does not exist in "Main"', out.getvalue())

        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Article "it-gets-better" does not exist in'
                      ' "main1-1.localhost"', out.getvalue())

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        article = self.mk_article(
            self.yourmind, title='it gets better', slug='it-gets-better')
        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Image "01_happygirl_feature_It gets better"'
                      ' does not exist in "main1"', out.getvalue())

        Image.objects.create(
            title="01_happygirl_feature_It gets better.jpg",
            file=get_test_image_file(),
        )
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        article.refresh_from_db()
        self.assertEqual(str(article.image),
                         "01_happygirl_feature_It gets better.jpg")

    def test_remove_placeholder_text_from_comments(self):
        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind')
        article = self.mk_article(
            self.yourmind, title='it gets better', slug='it-gets-better')

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="comment without place holder text",
            submit_date=timezone.now())

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="Type your comment here...comment with placeholder text",
            submit_date=timezone.now())

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="some text before theplaceholder"
            " Type your comment here...more text after the place holder",
            submit_date=timezone.now())

        call_command(
            'remove_placeholder_text_from_comments',
            'Type your comment here...'
        )

        for comment in Comment.objects.all().iterator():
            self.assertNotIn(comment.comment, 'Type your comment here...')

    def test_change_content_language(self):
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='es',
            is_active=True)
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your Mind')
        self.yourmind3 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind 2')
        self.tag = self.mk_tag(
            SectionIndexPage.objects.child_of(self.main).first())
        self.tag2 = self.mk_tag(
            SectionIndexPage.objects.child_of(self.main).first())
        # make articles of different sections
        self.mk_articles(self.yourmind2, count=5)
        self.mk_articles(self.yourmind3, count=5)

        # translate the article into those languages
        self.mk_section_translation(self.yourmind2, self.french)
        self.mk_tag_translation(self.tag, self.french)
        articles = ArticlePage.objects.all()[1::2]
        for article in articles:
            self.mk_article_translation(article, self.french)
        fr_pk = self.french.pk
        sp_pk = self.spanish.pk

        fr_articles = [article.title for article in
                       ArticlePage.objects.filter(language=self.french)]
        fr_tags = [tag.title for tag in
                   Tag.objects.filter(language=self.french)]

        fr_sections = [section.title for section in
                       SectionPage.objects.filter(language=self.french)]

        out = StringIO()
        call_command(
            'change_content_language',
            fr_pk, sp_pk, stdout=out
        )
        self.assertEqual('', out.getvalue())
        # test that only the correct articles are translated
        sp_articles = [article.title for article in
                       ArticlePage.objects.filter(language=self.spanish)]

        sp_tags = [tag.title for tag in
                   Tag.objects.filter(language=self.spanish)]

        sp_sections = [section.title for section in
                       SectionPage.objects.filter(language=self.spanish)]

        self.assertEqual(sp_articles, fr_articles)
        self.assertEqual(sp_tags, fr_tags)
        self.assertEqual(sp_sections, fr_sections)

    def test_change_content_language__invalid_languages(self):
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your Mind')
        self.yourmind3 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind 2')
        # make articles of different sections
        self.mk_articles(self.yourmind2, count=5)
        self.mk_articles(self.yourmind3, count=5)

        # translate the article into those languages
        out = StringIO()
        call_command(
            'change_content_language',
            None, None, stdout=out
        )
        self.assertNotEqual('', out.getvalue())


class AddDefaultTagsTest(TestCase):
    def test_command_works(self):
        call_command('add_default_tags')


class AddDefaultTagsToArticlesTest(TestCase):
    def test_command_works(self):
        csv_file = join('gem', 'tests', 'fixtures',
                        'add_default_tags_to_articles.csv')
        call_command('add_default_tags_to_articles', csv_file, 'en')


class AddImagesToSectionsTest(TestCase, GemTestCaseMixin):
    def test_command_works(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        call_command('add_images_to_sections', 'en')
