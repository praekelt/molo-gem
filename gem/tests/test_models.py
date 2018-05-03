# coding=utf-8
import pytest

from copy import deepcopy

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from wagtail.wagtailcore.models import Site

from molo.core.models import (
    SiteLanguageRelation, Main, Languages, SiteSettings)
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (
    MoloSurveyPage, MoloSurveyFormField, SurveysIndexPage)
from gem.models import GemSettings, GemUserProfile

from os.path import join


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)
        self.survey_index = SurveysIndexPage.objects.first()
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')
        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()

    def test_partner_credit(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'Thank You')
        self.assertNotContains(response, 'https://www.google.co.za/')

        default_site = Site.objects.get(is_default_site=True)
        setting = GemSettings.for_site(default_site)
        setting.show_partner_credit = True
        setting.partner_credit_description = "Thank You"
        setting.partner_credit_link = "https://www.google.co.za/"
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'Thank You')
        self.assertContains(response, 'https://www.google.co.za/')

    def test_show_join_banner(self):
        template_settings = deepcopy(settings.TEMPLATES)
        template_settings[0]['DIRS'] = [
            join(
                settings.PROJECT_ROOT, 'templates',
                '_layout_specific_templates', 'springster',
            )
        ]

        with self.settings(TEMPLATES=template_settings):
            molo_survey_page = MoloSurveyPage(
                title='survey title',
                slug='survey-slug',
                homepage_introduction='Introduction to Test Survey ...',
                thank_you_text='Thank you for taking the Test Survey',
            )

            self.survey_index.add_child(instance=molo_survey_page)
            MoloSurveyFormField.objects.create(
                page=molo_survey_page,
                sort_order=1,
                label='Your favourite animal',
                field_type='singleline',
                required=True
            )
            setting = GemSettings.for_site(self.main.get_site())
            self.assertFalse(setting.show_join_banner)
            response = self.client.get('%s?next=%s' % (
                reverse('molo.profiles:auth_logout'),
                reverse('molo.profiles:user_register')))
            response = self.client.get('/')
            self.assertNotContains(
                response,
                "Share your opinions and stories, take polls, win fun prizes.")
            setting.show_join_banner = True
            setting.save()

            response = self.client.get('/')
            self.assertContains(
                response,
                "Share your opinions and stories, take polls, win fun prizes.")


class TestGemUserProfile(TestCase, MoloTestCaseMixin):
    def test_security_questions_check(self):
        self.mk_main()
        get_user_model().objects.create_user(
            username='user', email='user@example.com', password='pass')
        profile = GemUserProfile.objects.first()
        profile.set_security_question_1_answer('Answer 1')
        profile.set_security_question_2_answer('Answer 2')

        self.assertTrue(profile.check_security_question_1_answer('Answer 1'))
        self.assertTrue(profile.check_security_question_2_answer('Answer 2'))
