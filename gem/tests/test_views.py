from os.path import join
from copy import deepcopy

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User, Permission, Group
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client

from molo.core.models import (
    Main, SectionIndexPage)
from molo.profiles.models import (
    SecurityAnswer,
    SecurityQuestion,
    SecurityQuestionIndexPage,
    UserProfile,
    UserProfilesSettings,
)

from molo.commenting.forms import MoloCommentForm
from molo.commenting.models import MoloComment

from molo.forms.tests.base import create_molo_form_page
from molo.forms.models import (
   ArticlePageForms, FormsIndexPage,
   MoloFormSubmission, MoloFormField)

from gem.forms import GemRegistrationForm, GemEditProfileForm
from gem.models import GemSettings, GemCommentReport
from gem.tests.base import GemTestCaseMixin


@override_settings(
    SECURITY_QUESTION_1='question_1',
    SECURITY_QUESTION_2='question_2',
)
class GemRegistrationViewTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        for main in Main.objects.all():
            profile_settings = UserProfilesSettings.for_site(main.get_site())
            profile_settings.show_security_question_fields = True
            profile_settings.security_questions_required = True
            profile_settings.num_security_questions = 2
            profile_settings.activate_gender = True
            profile_settings.capture_gender_on_reg = True
            profile_settings.gender_required = True
            profile_settings.save()

            security_index = SecurityQuestionIndexPage.objects.descendant_of(
                main).first()
            for i in range(1, 3):
                question = SecurityQuestion(title='question_{0}'.format(i))
                security_index.add_child(instance=question)
                question.save_revision().publish()

    def user_registration_data(self):
        return {
            'username': 'testuser',
            'password': '1234',
            'gender': 'f',
            'question_0': 'answer_1',
            'question_1': 'answer_2',
            'terms_and_conditions': 'on',
        }

    def test_register_view(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue(isinstance(response.context['form'],
                        GemRegistrationForm))

    def test_register_view_valid_form(self):
        self.assertEqual(UserProfile.objects.all().count(), 0)
        self.client.post(reverse('user_register'), {
            'username': 'testuser',
            'password': '1234',
            'gender': 'f',
            'question_0': 'answer_1',
            'question_1': 'answer_2',
            'terms_and_conditions': 'on',
        })
        self.assertEqual(UserProfile.objects.all().count(), 1)
        user = User.objects.get(username='testuser')

        # test thatthe registrationv view writes to both gem and molo profiles
        self.assertEqual(user.profile.gender, 'f')

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'question_0',
            ['This field is required.']
        )
        self.assertFormError(
            response, 'form', 'question_1',
            ['This field is required.']
        )

    def test_email_or_phone_not_allowed_in_username(self):
        response = self.client.post(reverse('user_register'), {
            'username': 'tester@test.com',
            'password': '1234',
            'gender': 'm',
            'question_0': 'cat',
            'question_1': 'dog'
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#x27;t use your" \
                                      " email address or phone number in" \
                                      " your username."

        self.assertContains(response, expected_validation_message)

        response = self.client.post(reverse('user_register'), {
            'username': '0821231234',
            'password': '1234',
            'gender': 'm',
            'question_0': 'cat',
            'question_1': 'dog'
        })

        self.assertContains(response, expected_validation_message)

    def test_successful_login_for_migrated_users(self):
        user = User.objects.create_user(
            username='1_newuser',
            email='newuser@example.com',
            password='newuser')
        user.profile.migrated_username = 'newuser'
        user.profile.site = self.main.get_site()
        user.profile.save()

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser',
        })
        self.assertRedirects(response, '/')

        client = Client(HTTP_HOST=self.main2.get_site().hostname)

        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser',
        })
        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

    def test_successful_login_for_migrated_users_in_site_2(self):
        user_site_1 = User.objects.create_user(
            username='1_newuser',
            email='newuser@example.com',
            password='newuser1')
        user_site_1.profile.migrated_username = 'newuser'
        user_site_1.profile.site = self.main.get_site()
        user_site_1.profile.save()

        user_site_2 = User.objects.create_user(
            username='2_newuser',
            email='newuser@example.com',
            password='newuser2')
        user_site_2.profile.migrated_username = 'newuser'
        user_site_2.profile.site = self.main2.get_site()
        user_site_2.profile.save()

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser1',
        })
        self.assertRedirects(response, '/')

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser2',
        })
        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

        client = Client(HTTP_HOST=self.main2.get_site().hostname)

        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser2',
        })
        self.assertRedirects(response, '/')
        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser1',
        })

        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

    def test_registration_creates_security_answer(self):
        self.client.post(
            reverse('user_register'),
            self.user_registration_data(),
        )

        security_questions = SecurityQuestion.objects.descendant_of(
            self.main).all()
        security_answers = SecurityAnswer.objects.all()

        self.assertEqual(security_answers.count(), 2)
        self.assertEqual(
            security_answers.first().question,
            security_questions.first(),
        )
        self.assertEqual(
            security_answers.first().user,
            User.objects.get(username='testuser').profile,
        )
        self.assertEqual(
            security_answers.first().check_answer('answer_1'),
            True,
        )
        self.assertEqual(
            security_answers.last().check_answer('answer_2'),
            True,
        )

    def test_security_answer_attached_to_question_from_correct_site(self):
        client = Client(HTTP_HOST=self.main2.get_site().hostname)
        client.post(
            reverse('user_register'),
            self.user_registration_data(),
        )
        security_questions = SecurityQuestion.objects.descendant_of(
            self.main2).all()
        security_answers = SecurityAnswer.objects.all()

        for i in range(2):
            self.assertEqual(
                security_answers[i].question,
                security_questions[i],
            )


class GemEditProfileViewTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.client.login(username='tester', password='tester')

    def test_edit_profile_view_uses_correct_form(self):
        response = self.client.get(reverse('edit_my_profile'))
        self.assertTrue(isinstance(response.context['form'],
                                   GemEditProfileForm))

    def test_email_or_phone_not_allowed_in_display_name(self):
        response = self.client.post(reverse('edit_my_profile'), {
            'alias': 'tester@test.com'
        })
        expected_validation_message = "Sorry, but that is an invalid display" \
                                      " name. Please don&#x27;t use your" \
                                      " email address or phone number in" \
                                      " your display name."
        self.assertContains(response, expected_validation_message)

        response = self.client.post(reverse('edit_my_profile'), {
            'alias': '0821231234'
        })

        self.assertContains(response, expected_validation_message)

    def test_offensive_language_not_allowed_in_display_name(self):
        gem_settings, created = GemSettings.objects.get_or_create(
            site_id=Main.objects.first().get_site().pk,
            banned_names_with_offensive_language='naughty')
        response = self.client.post(reverse('edit_my_profile'), {
            'alias': 'naughty'
        })
        expected_validation_message = (
            "Sorry, the name you have used is not allowed. "
            "Please, use a different name for your display name.")
        self.assertContains(response, expected_validation_message)


class CommentingTestCase(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin')

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        self.article = self.mk_article(self.yourmind,
                                       title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

    def create_comment(self, article, comment, user, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def getData(self):
        return {
            'name': self.user.username,
            'email': self.user.email
        }

    def test_comment_shows_user_display_name(self):
        # check when user doesn't have an alias
        self.create_comment(self.article, 'test comment1 text', self.user)
        response = self.client.get('/sections-main1-1/your-mind/article-1/')
        self.assertContains(response, "Anonymous")

        # check when user have an alias
        self.user.profile.alias = 'this is my alias'
        self.user.profile.save()
        self.create_comment(self.article, 'test comment2 text', self.user)
        response = self.client.get('/sections-main1-1/your-mind/article-1/')
        self.assertContains(response, "this is my alias")
        self.assertNotContains(response, "tester")

    def test_anonymous_comment_with_alias(self):
        self.client.login(username='tester', password='tester')
        self.user.profile.alias = 'this is my alias'
        self.user.profile.save()
        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'comment': 'Foo',
            'submit_anonymously': '1',
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        comment = MoloComment.objects.filter(user=self.user).first()
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'Anonymous')

    def test_comment_distinguishes_moderator_user(self):
        self.user = User.objects.create_user(
            username='foo',
            email='foo@example.com',
            password='foo',
            is_staff=True)

        self.client.login(username='admin', password='admin')

        response = self.client.get('/sections-main1-1/your-mind/article-1/')
        self.assertNotContains(response, "Big Sister")
        self.assertNotContains(response, "Gabi")

        self.create_comment(self.article, 'test comment1 text', self.superuser)
        response = self.client.get('/sections-main1-1/your-mind/article-1/')
        self.assertContains(response, "Big Sister")
        self.assertNotContains(response, "Gabi")

        setting = GemSettings.objects.get(
            site_id=self.main.get_site().pk)
        setting.moderator_name = 'Gabi'
        setting.save()
        response = self.client.get('/sections-main1-1/your-mind/article-1/')
        self.assertNotContains(response, "Big Sister")
        self.assertContains(response, "Gabi")

    def test_moderator_user_contact_information_comment(self):
        self.client.login(username='admin', password='admin')

        self.create_comment(
            self.article, 'test comment1 text', self.superuser)

        email = 'someone1@test.com'
        url = '/admin/comment/1/reply/'
        content_type = '{}.{}'.format(
            *self.article.specific.content_type.natural_key())
        response = self.client.get(url)

        data = response.context_data['form'].initial
        data.update(dict(
            comment=email,
            object_pk=self.article.pk,
            content_type=content_type
        ))

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/commenting/molocomment/')

    def get_admin_perms(self):
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        return admin_permission

    def test_non_moderator_user_contact_information_comment(self):
        user = User.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            is_staff=True,
            password='tester')
        admin_permission = self.get_admin_perms()
        user.user_permissions.add(admin_permission)
        user.profile.admin_sites.add(self.main.get_site())

        self.assertTrue(user.has_perm('wagtailadmin.access_admin'))
        self.client.force_login(user)

        self.create_comment(
            self.article, 'test comment1 text', self.superuser)

        email = 'someone1@test.com'
        url = '/admin/comment/1/reply/'
        content_type = '{}.{}'.format(
            *self.article.specific.content_type.natural_key())
        response = self.client.get(url)

        data = response.context_data['form'].initial
        data.update(dict(
            comment=email,
            object_pk=self.article.pk,
            content_type=content_type
        ))

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {'comment': [
                'This comment has been removed as it contains profanity, '
                'contact information or other inappropriate content. '
            ]}
        )

        group, created = Group.objects.get_or_create(
            name='comment_moderator')
        user.groups.add(group)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/commenting/molocomment/')

    def getValidData(self, obj):
        form = MoloCommentForm(obj)
        form_data = self.getData()
        form_data.update(form.initial)
        return form_data

    def test_comment_filters(self):
        GemSettings.objects.create(site_id=Main.objects.first().get_site().pk,
                                   banned_keywords_and_patterns='naughty')

        form_data = self.getValidData(self.article)

        # check if user has typed in a number
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="0821111111")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has typed in an email address
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="test@test.com")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has used a banned keyword
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="naughty")
        )

        self.assertFalse(comment_form.is_valid())


class GemFeedViewsTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.section = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Test Section')

        self.article_page = self.mk_article(
            self.section, title='Test Article',
            subtitle='This should appear in the feed')

    def test_rss_feed_view(self):
        response = self.client.get(reverse('feed_rss'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')

    def test_atom_feed_view(self):
        response = self.client.get(reverse('feed_atom'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')


class GemReportCommentViewTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin')

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        self.article = self.mk_article(self.yourmind,
                                       title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

        self.client.login(username='tester', password='tester')

        self.content_type = ContentType.objects.get_for_model(self.user)

    def create_comment(self, article, comment, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def create_reported_comment(self, comment, report_reason):
        return GemCommentReport.objects.create(
            comment=comment,
            user=self.user,
            reported_reason=report_reason
        )

    def test_report_view(self):
        comment = self.create_comment(self.article, 'report me')
        response = self.client.get(
            reverse('report_comment', args=(comment.pk,))
        )

        self.assertContains(response, 'Please let us know why you are '
                                      'reporting this comment?')

    def test_user_has_already_reported_comment(self):
        comment = self.create_comment(self.article, 'report me')

        self.create_reported_comment(comment, 'Spam')

        response = self.client.get(
            reverse('report_comment', args=(comment.pk,)), follow=True
        )

        self.assertContains(response, 'You have already reported this comment')

    def test_renders_report_response_template(self):
        comment = self.create_comment(self.article, 'report me')
        response = self.client.get(
            reverse('report_response', args=(comment.pk,)))
        self.assertContains(response, 'This comment has been reported.')


class TestServiceRedirectView(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

    def test_redirect_view(self):
        res = self.client.get(reverse('services_redirect'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/sections/service-finder/')


# THE REACTION QUESTIONS ON FORMS IS NOW
# SIMILAR TO THE POLLS IMPLEMENATION ON
# FORMS HOWEVER USES A DIFFERENT TAG
# FROM display_form_directly -
# DO THESE BELOW TEST NEED TO BE ADJUSTED
# - Aphiwe to please advice?
class ChhaaJaaReactionQuestionsTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.section_index = SectionIndexPage.objects.child_of(
            self.main).last()
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

    def test_reaction_question(self):
        template_settings = deepcopy(settings.TEMPLATES)
        template_settings[0]['DIRS'] = [
            join(settings.PROJECT_ROOT, 'templates', 'chhaajaa')
        ]

        with self.settings(TEMPLATES=template_settings):
            self.client.force_login(self.user)
            promote_date = timezone.now() + timezone.timedelta(days=-1)
            demote_date = timezone.now() + timezone.timedelta(days=1)
            article = self.mk_article(
                self.yourmind,
                feature_as_hero_article=True,
                promote_date=promote_date,
                demote_date=demote_date
            )
            forms_index = FormsIndexPage.objects.filter().first()
            form = create_molo_form_page(
                forms_index, display_form_directly=True)

            form_field = MoloFormField.objects.create(
                page=form, sort_order=1, label='q1', field_type='checkboxes',
                required=True, page_break=False,
                admin_label='q1', skip_logic=None, choices='a,b,c',
            )
            ArticlePageForms.objects.create(
                page=article, form=form)

            res = self.client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, article.title)
            # self.assertTrue(form_field.label in str(res.content))
            # now the user is redirected to the form page
            self.assertTrue(
                '<a href="#survey-form" class="vote__icon">Poll</a>',
                str(res.content)
            )

            data = {
                form_field.admin_label: 'b'
            }
            MoloFormSubmission.objects.create(
                page=form, article_page=article,
                user=self.user, form_data=data
            )

            res = self.client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, article.title)
            self.assertTrue(
                '<a href="#survey-form" class="vote__icon">Poll</a>',
                str(res.content)
            )

    def test_reaction_question_multi_submissions(self):
        template_settings = deepcopy(settings.TEMPLATES)
        template_settings[0]['DIRS'] = [
            join(settings.PROJECT_ROOT, 'templates', 'chhaajaa')
        ]

        with self.settings(TEMPLATES=template_settings):
            self.client.force_login(self.user)
            promote_date = timezone.now() + timezone.timedelta(days=-1)
            demote_date = timezone.now() + timezone.timedelta(days=1)
            article = self.mk_article(
                self.yourmind,
                feature_as_hero_article=True,
                promote_date=promote_date,
                demote_date=demote_date
            )
            forms_index = FormsIndexPage.objects.filter().first()
            form = create_molo_form_page(
                forms_index, display_form_directly=True,
                allow_multiple_submissions_per_user=True)

            form_field = MoloFormField.objects.create(
                page=form, sort_order=1, label='q1', field_type='checkboxes',
                required=True, page_break=False,
                admin_label='q1', skip_logic=None, choices='a,b,c',
            )
            ArticlePageForms.objects.create(
                page=article, form=form)

            res = self.client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, article.title)
            # self.assertTrue(form_field.label in str(res.content))
            self.assertTrue(
                '<a href="#survey-form" class="vote__icon">Poll</a>',
                str(res.content)
            )

            data = {
                form_field.admin_label: 'b'
            }
            MoloFormSubmission.objects.create(
                page=form, article_page=article,
                user=self.user, form_data=data
            )

            res = self.client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, article.title)
            self.assertTrue(
                '<a href="#survey-form" class="vote__icon">Poll</a>',
                str(res.content)
            )
