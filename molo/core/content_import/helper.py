import json

from django.shortcuts import get_object_or_404

from molo.core.models import (
    Main, SiteLanguage, PageTranslation, SectionPage, ArticlePage, FooterPage)

from unicore.content.models import Category, Page


class ContentImportHelper(object):

    def __init__(self, ws):
        self.ws = ws

    def get_or_create(self, cls, obj, parent):
        if cls.objects.filter(uuid=obj.uuid).exists():
            return cls.objects.get(uuid=obj.uuid)

        instance = cls(uuid=obj.uuid, title=obj.title)
        parent.add_child(instance=instance)
        print 'created', obj.title
        return instance

    def get_or_create_translation(self, cls, obj, parent, language):
        if cls.objects.filter(uuid=obj.uuid).exists():
            return cls.objects.get(uuid=obj.uuid)

        instance = cls(uuid=obj.uuid, title=obj.title)
        parent.add_child(instance=instance)
        language_relation = instance.languages.first()
        language_relation.language = language
        language_relation.save()
        print 'created translation', obj.title
        return instance

    def import_section_content(self, c, site_language):
        main = Main.objects.all().first()
        if site_language.is_main_language:
            section = self.get_or_create(SectionPage, c, main)
        else:
            section = self.get_or_create_translation(
                SectionPage, c, main, site_language)

        section.description = c.subtitle
        # TODO: image
        section.save_revision().publish()

        return section

    def import_page_content(self, p, site_language, main_instance):
        if site_language.is_main_language:
            if p.primary_category:
                try:
                    section = SectionPage.objects.get(
                        uuid=p.primary_category)
                    page = self.get_or_create(ArticlePage, p, section)
                except SectionPage.DoesNotExist:
                    print "couldn't find", p.primary_category, (
                        SectionPage.objects.all().values('uuid'))
            else:
                # special case for articles with no primary category
                # this assumption is probably wrong..
                # but we have no where else to put them
                main = Main.objects.all().first()
                page = self.get_or_create(FooterPage, p, main)
        else:
            parent = main_instance.get_parent()
            page = self.get_or_create_translation(
                main_instance.__class__, p, parent, site_language)

        page.subtitle = p.subtitle
        page.body = json.dumps([
            {'type': 'paragraph', 'value': p.description},
            {'type': 'paragraph', 'value': p.content}
        ])
        is_featured = p.featured if p.featured else False
        is_featured_in_category = p.featured_in_category \
            if p.featured_in_category else False

        page.featured_in_latest = is_featured
        page.featured_in_homepage = is_featured_in_category
        # TODO: tags (see mk_tags)
        # TODO: related pages
        # TODO: image
        page.save_revision().publish()

        return page

    def import_main_language_content(self, selected_locale, site_language):
        for c in self.ws.S(Category).filter(
                language=selected_locale.get('locale')
        ).order_by('position')[:10000]:
            # S() only returns 10 results if you don't ask for more

            self.import_section_content(c, site_language)

        for p in self.ws.S(Page).filter(
            language=selected_locale.get('locale')
        ).order_by('position')[:10000]:
            # S() only returns 10 results if you don't ask for more

            self.import_page_content(p, site_language, 'foo')

    def import_translated_content(self, selected_locale, site_language):
        for tc in self.ws.S(Category).filter(
            language=selected_locale.get('locale')
        ).order_by('position')[:10000]:
            # S() only returns 10 results if you don't ask for more
            translated_section = self.import_section_content(
                tc, site_language)
            if tc.source:
                try:
                    parent = SectionPage.objects.get(
                        uuid=tc.source)
                    PageTranslation.objects.get_or_create(
                        page=parent,
                        translated_page=translated_section)
                except SectionPage.DoesNotExist:
                    print "couldn't find", tc.source, (
                        SectionPage.objects.all().values('uuid'))
            else:
                print "no source found for: ", tc.source, (
                    SectionPage.objects.all().values('uuid'))

        for tp in self.ws.S(Page).filter(
            language=selected_locale.get('locale')
        ).order_by('position')[:10000]:
            # S() only returns 10 results if you don't ask for more
            try:
                main_instance = ArticlePage.objects.get(
                    uuid=tp.source)
                page = self.import_page_content(
                    tp, site_language, main_instance)
                PageTranslation.objects.get_or_create(
                    page=main_instance,
                    translated_page=page)
            except ArticlePage.DoesNotExist:
                print "No source found for: ", tp.source, (
                    ArticlePage.objects.all().values('uuid'))

    def import_content_for(self, locales):
        for selected_locale in locales:
            site_language = get_object_or_404(
                SiteLanguage, locale=selected_locale.get('site_language'))

            if site_language.is_main_language:
                self.import_main_language_content(
                    selected_locale, site_language)
            else:
                self.import_translated_content(selected_locale, site_language)
