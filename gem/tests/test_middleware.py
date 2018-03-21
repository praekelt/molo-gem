from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase, override_settings
from django.test.client import Client

from gem.middleware import AdminRedirectHTTPS, GemMoloGoogleAnalyticsMiddleware
from gem.models import GemSettings

from mock import patch

from molo.core.models import SiteSettings
from molo.core.tests.base import MoloTestCaseMixin


class TestCustomGemMiddleware(TestCase, MoloTestCaseMixin):

    submit_tracking_method = (
        "gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking"
    )

    def setUp(self):
        self.client = Client()
        self.mk_main()

        self.site_settings = SiteSettings.for_site(self.site)
        self.site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        self.site_settings.save()

        GemSettings.objects.create(
            site_id=self.site.id,
            bbm_ga_account_subdomain='bbm',
            bbm_ga_tracking_code='bbm_tracking_code',
        )

        self.response = self.client.get('/')

    @patch(submit_tracking_method)
    def test_submit_to_additional_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL contains the
        bbm_ga_account_subdomain, info should be sent to
        the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='bbm.example.com')
        request.site = self.site

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code', request, self.response)

    @patch(submit_tracking_method)
    def test_submit_to_bbm_analytics_if_cookie_set(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the BBM cookie is set, info
        should be sent to the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='example.com')
        request.COOKIES['bbm'] = 'true'
        request.site = self.site

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code', request, self.response)

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL does not contain the
        bbm_ga_account_subdomain, info should be sent to
        the local GA account, not the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='example.com')
        request.site = self.site

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code', request, self.response)


@override_settings(ADMIN_REDIRECT_HTTPS=True)
class TestAdminRedirectHTTPSMiddleware(TestCase):
    def setUp(self):
        self.middleware = AdminRedirectHTTPS()

    def test_should_do_nothing_if_not_admin_page(self):
        request = RequestFactory().get('/')
        return_value = self.middleware.process_request(request)
        self.assertEqual(return_value, None)

    @override_settings(ADMIN_REDIRECT_HTTPS=False)
    def test_should_do_nothing_if_setting_disabled(self):
        request = RequestFactory().get('/admin/')
        return_value = self.middleware.process_request(request)
        self.assertEqual(return_value, None)

    def test_should_do_nothing_if_scheme_not_http(self):
        request = RequestFactory().get('/admin/', secure=True)
        return_value = self.middleware.process_request(request)
        self.assertEqual(return_value, None)

    def test_should_redirect_admin_requests_to_https(self):
        request = RequestFactory().get('/admin/path/')
        return_value = self.middleware.process_request(request)
        self.assertTrue(isinstance(return_value, HttpResponseRedirect))
        self.assertEqual(return_value.url, 'https://testserver/admin/path/')

    def test_should_redirect_django_admin_requests_to_https(self):
        request = RequestFactory().get('/django-admin/path/')
        return_value = self.middleware.process_request(request)
        self.assertTrue(isinstance(return_value, HttpResponseRedirect))
        self.assertEqual(
            return_value.url,
            'https://testserver/django-admin/path/',
        )
