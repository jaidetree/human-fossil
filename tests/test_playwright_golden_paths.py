"""Browser-level Playwright e2e coverage for the golden paths (ticket 17)
across the full page set: Home -> Works browsing, a Work's gallery, the
Contact form, and a Resource download from the Home page's footer.

These exercise the real rendered pages end-to-end — a live Django server
(`live_server`, pytest-django) driven by a real Chromium browser
(`page`, pytest-playwright) — rather than views/templates in isolation
(covered separately in `human_fossil/tests/`).
"""

import importlib

import pytest
from django.test import override_settings
from playwright.sync_api import expect

import config.urls as urls_module
from human_fossil.tests.factories import ResourceFactory, WorkFactory, WorkImageFactory

TEST_EMAIL_BACKEND = "anymail.backends.test.EmailBackend"


@pytest.fixture
def local_media_serving(settings):
    """Make local MEDIA_ROOT fetchable over the live server for this test only.

    `config/urls.py` only appends the local-media `static()` patterns when
    `DEBUG` is True — production always serves media from Cloudflare R2 (ticket
    16), so that gate is dev/test-only convenience and stays untouched in
    `config/settings.py`. Verifying an actual Resource download needs the file
    reachable over HTTP, so flip `DEBUG` on and reload the already-imported
    urlconf module for the duration of this test, then put both back — this
    only affects this process's in-memory urlconf, not the settings file.
    """
    settings.DEBUG = True
    importlib.reload(urls_module)
    from django.urls import clear_url_caches

    clear_url_caches()
    yield
    settings.DEBUG = False
    importlib.reload(urls_module)
    clear_url_caches()


@pytest.mark.django_db(transaction=True)
def test_home_to_works_browsing(live_server, page):
    """Home's hero links to the Works listing, and the Works showcase teaser
    links through to a Work's detail page."""
    work = WorkFactory(title="Gowanus Tote", published=True, featured=True)
    WorkImageFactory(work=work, order=1)

    page.goto(live_server.url + "/")
    page.get_by_role("link", name="View the Portfolio").click()
    expect(page).to_have_url(live_server.url + "/works/")

    page.locator("a", has_text="Gowanus Tote").first.click()
    expect(page).to_have_url(live_server.url + f"/works/{work.slug}/")
    expect(page.get_by_role("heading", name="Gowanus Tote")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_work_gallery_shows_images_in_order_with_captions(live_server, page):
    """A Work's full gallery renders every image in `order`, with Markdown
    captions rendered to HTML."""
    work = WorkFactory(title="Leather Satchel", published=True)
    WorkImageFactory(work=work, order=1, caption="Front view")
    WorkImageFactory(work=work, order=2, caption="**Interior** pocket")

    page.goto(live_server.url + f"/works/{work.slug}/")

    images = page.locator(".work-gallery-image")
    expect(images).to_have_count(2)
    assert "Front view" in images.nth(0).inner_text()
    assert "Interior pocket" in images.nth(1).inner_text()
    # Markdown caption rendered as HTML, not shown raw.
    expect(images.nth(1).locator("strong")).to_have_text("Interior")


@pytest.mark.django_db(transaction=True)
@override_settings(EMAIL_BACKEND=TEST_EMAIL_BACKEND)
def test_contact_form_submission_shows_success_state(live_server, mailoutbox, page):
    """A valid Contact form submission shows the success state. The Anymail
    test/dummy backend captures the notification in `mailoutbox` instead of
    sending anything real."""
    page.goto(live_server.url + "/contact/")
    page.fill('input[name="name"]', "Jamie Visitor")
    page.fill('input[name="email"]', "jamie@example.com")
    page.select_option('select[name="subject"]', "Business Inquiry")
    page.fill('textarea[name="message"]', "Interested in a custom bag.")
    page.click('button[type="submit"]')

    expect(page.get_by_text("Thanks for reaching out")).to_be_visible()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["hello@human-fossil.com"]


@pytest.mark.django_db(transaction=True)
def test_resource_download_from_home_footer(live_server, local_media_serving, page):
    """Clicking a Resource link in the Home page's Resources footer section
    downloads the attached file directly — there is no separate `/resources`
    listing page in this project."""
    resource = ResourceFactory(
        title="Pattern Template",
        published=True,
        featured=True,
        file__filename="pattern-template.zip",
        file__data=b"PK\x03\x04fake-zip-content-for-testing",
    )

    page.goto(live_server.url + "/")
    link = page.get_by_role("link", name="Pattern Template")
    expect(link).to_be_visible()

    with page.expect_download() as download_info:
        link.click()
    download = download_info.value

    # `FileSystemStorage.get_available_name` disambiguates on a filename
    # clash with a previous test run's leftover upload (`file_overwrite` is
    # only configured for the R2 backend), so assert against the name Django
    # actually saved rather than the literal filename passed to the factory.
    saved_filename = resource.file.name.rsplit("/", 1)[-1]
    assert download.suggested_filename == saved_filename
    assert download.path().read_bytes() == b"PK\x03\x04fake-zip-content-for-testing"
