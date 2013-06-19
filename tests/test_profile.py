#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time
import pytest
from unittestzero import Assert

from pages.home_page import Home
from pages.register import ProfileTab
from tests.base_test import BaseTest


class TestProfile(BaseTest):

    @pytest.mark.nondestructive
    def test_profile_deletion_confirmation(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()
        edit_profile_page = home_page.header.click_edit_profile_menu_item()
        confirm_profile_delete_page = edit_profile_page.click_delete_profile_button()
        Assert.true(confirm_profile_delete_page.is_csrf_token_present)
        Assert.true(confirm_profile_delete_page.is_confirm_text_present)
        Assert.true(confirm_profile_delete_page.is_cancel_button_present)
        Assert.true(confirm_profile_delete_page.is_delete_button_present)

    @pytest.mark.xfail(reason='Bug 883194 - Error message appears when trying to save changes in Edit Profile page')
    def test_edit_profile_information(self, mozwebqa):
        home_page = Home(mozwebqa)

        home_page.login()

        edit_profile_page = home_page.header.click_edit_profile_menu_item()
        Assert.true(edit_profile_page.is_csrf_token_present)
        current_time = str(time.time()).split('.')[0]
        new_full_name = "Updated Mozillians User %s" % current_time
        new_biography = "Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, most likely, run at %s" % current_time
        new_website = "http://%s.com/" % current_time
        edit_profile_page.set_full_name(new_full_name)
        edit_profile_page.set_website(new_website)
        edit_profile_page.set_bio(new_biography)
        profile_page = edit_profile_page.click_update_button()
        name = profile_page.name
        biography = profile_page.biography
        website = profile_page.website
        Assert.equal(name, new_full_name)
        Assert.equal(biography, new_biography)
        Assert.equal(website, new_website)

    @pytest.mark.nondestructive
    @pytest.mark.xfail(reason="This is no longer applicable, browserid link not present in edit profile page")
    def test_browserid_link_present(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()
        edit_profile_page = home_page.header.click_edit_profile_menu_item()
        Assert.true(edit_profile_page.is_browserid_link_present)

    @pytest.mark.xfail(reason="Bug 797790 - Create Your Profile page privacy policy error message is ambiguous")
    def test_creating_profile_without_checking_privacy_policy_checkbox(self, mozwebqa):
        user = self.get_new_user()

        home_page = Home(mozwebqa)

        profile = home_page.create_new_user(user)

        profile.set_full_name("User that doesn't like policy")
        profile.set_bio("Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, and will not check accept the privacy policy")

        skills = profile.click_next_button()
        skills.add_skill('test')
        skills.add_language('english')

        location = skills.click_next_button()
        location.select_country('us')
        location.set_state('California')
        location.set_city('Mountain View')

        location.click_create_profile_button()

        profile = ProfileTab(mozwebqa)

        Assert.equal('new error message', profile.error_message)
        location = profile.go_to_tab('location')
        Assert.equal('This field is required.', location.privacy_error_message)

    def test_profile_creation(self, mozwebqa):
        user = self.get_new_user()

        home_page = Home(mozwebqa)

        profile = home_page.create_new_user(user)

        profile.set_full_name("New MozilliansUser")
        profile.set_bio("Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, most likely")

        skills = profile.click_next_button()
        skills.add_skill('test')
        skills.add_language('english')

        location = skills.click_next_button()
        location.select_country('us')
        location.set_state('California')
        location.set_city('Mountain View')
        location.check_privacy()

        profile_page = location.click_create_profile_button()

        Assert.true(profile_page.was_account_created_successfully)
        Assert.true(profile_page.is_pending_approval_visible)

        Assert.equal('New MozilliansUser', profile_page.name)
        Assert.equal(user['email'], profile_page.email)
        Assert.equal("Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, most likely", profile_page.biography)
        Assert.equal('test', profile_page.skills)
        Assert.equal('english', profile_page.languages)
        Assert.equal('Mountain View, California\nUnited States', profile_page.location)

    @pytest.mark.xfail(reason="Bug 835318 - Error adding groups / skills / or languages with non-latin chars.")
    def test_non_ascii_characters_are_allowed_in_profile_information(self, mozwebqa):
        user = self.get_new_user()

        home_page = Home(mozwebqa)
        profile = home_page.create_new_user(user)

        profile.set_full_name("New MozilliansUser")
        profile.set_bio("Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, most likely")

        skills = profile.click_next_button()
        skills.add_skill(u'\u0394\u03D4\u03D5\u03D7\u03C7\u03C9\u03CA\u03E2')
        skills.add_language(u'\u0394\u03D4\u03D5\u03D7\u03C7\u03C9\u03CA\u03E2')

        location = skills.click_next_button()
        location.select_country('gr')
        location.set_state('Greece')
        location.set_city('Athens')
        location.check_privacy()

        profile_page = location.click_create_profile_button()

        Assert.true(profile_page.was_account_created_successfully)
        Assert.true(profile_page.is_pending_approval_visible)

        Assert.equal('New MozilliansUser', profile_page.name)
        Assert.equal(user['email'], profile_page.email)
        Assert.equal("Hello, I'm new here and trying stuff out. Oh, and by the way: I'm a robot, run in a cronjob, most likely", profile_page.biography)
        Assert.equal(u'\u0394\u03D4\u03D5\u03D7\u03C7\u03C9\u03CA\u03E2', profile_page.skills)
        Assert.equal(u'\u0394\u03D4\u03D5\u03D7\u03C7\u03C9\u03CA\u03E2', profile_page.languages)
        Assert.equal('Athenes, Greece\nGreece', profile_page.location)

    @pytest.mark.nondestructive
    def test_that_filter_by_city_works(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()

        profile_page = home_page.open_user_profile(u'MozilliansUser')
        city = profile_page.city
        country = profile_page.country
        search_results_page = profile_page.click_city_name(city=city, country=country)
        expected_results_title = u'Mozillians in %s, %s' % (city, country)
        actual_results_title = search_results_page.title

        Assert.true(search_results_page.is_the_current_page)
        Assert.equal(
            expected_results_title, actual_results_title,
            u'''Search results title is incorrect.
                Expected: %s, but got: %s''' % (expected_results_title, actual_results_title))

        random_profile = search_results_page.get_random_profile()
        random_profile_city = random_profile.city

        Assert.equal(
            city, random_profile_city,
            u'Expected city: %s, but got: %s' % (city, random_profile_city))

    @pytest.mark.nondestructive
    def test_that_filter_by_region_works(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()

        profile_page = home_page.open_user_profile(u'MozilliansUser')
        region = profile_page.region
        country = profile_page.country
        search_results_page = profile_page.click_region_name(region=region, country=country)
        expected_results_title = u'Mozillians in %s, %s' % (region, country)
        actual_results_title = search_results_page.title

        Assert.true(search_results_page.is_the_current_page)
        Assert.equal(
            expected_results_title, actual_results_title,
            u'''Search results title is incorrect.
                Expected: %s, but got: %s''' % (expected_results_title, actual_results_title))

        random_profile = search_results_page.get_random_profile()
        random_profile_region = random_profile.region

        Assert.equal(
            region, random_profile_region,
            u'Expected region: %s, but got: %s' % (region, random_profile_region))

    @pytest.mark.nondestructive
    def test_that_filter_by_county_works(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()

        profile_page = home_page.open_user_profile(u'MozilliansUser')
        country = profile_page.country
        search_results_page = profile_page.click_country_name(country=country)
        expected_results_title = u'Mozillians in %s' % country
        actual_results_title = search_results_page.title

        Assert.true(search_results_page.is_the_current_page)
        Assert.equal(
            expected_results_title, actual_results_title,
            u'''Search results title is incorrect.
                Expected: %s, but got: %s''' % (expected_results_title, actual_results_title))

        random_profile = search_results_page.get_random_profile()
        random_profile_country = random_profile.country

        Assert.equal(
            country, random_profile_country,
            u'Expected country: %s, but got: %s' % (country, random_profile_country))
