import pytest
from django.db import IntegrityError

from apps.accounts.factories import UserFactory
from apps.core.factories import (
    DepartmentFactory,
    FAQFactory,
    SiteSettingFactory,
    TeamMemberFactory,
)
from apps.core.models import FAQ, FAQCategory, SiteSetting, TeamMember


@pytest.mark.django_db
class TestSoftDeleteViaUser:
    def test_soft_delete_sets_fields(self):
        user = UserFactory()
        user.soft_delete()
        user.refresh_from_db()
        assert user.is_deleted is True
        assert user.deleted_at is not None
        assert user.is_active is False

    def test_restore_clears_fields(self):
        user = UserFactory()
        user.soft_delete()
        user.restore()
        user.refresh_from_db()
        assert user.is_deleted is False
        assert user.deleted_at is None
        assert user.is_active is True


@pytest.mark.django_db
class TestFAQ:
    def test_ordering_by_category_then_order(self):
        user = UserFactory()
        faq_s = FAQFactory(category=FAQCategory.SERVICES, order=0, created_by=user)
        faq_g = FAQFactory(category=FAQCategory.GENERAL, order=1, created_by=user)
        result = list(FAQ.objects.all())
        assert result.index(faq_g) < result.index(faq_s)

    def test_str_returns_question(self):
        faq = FAQFactory()
        assert str(faq) == faq.question


@pytest.mark.django_db
class TestSiteSetting:
    def test_unique_key_constraint(self):
        SiteSettingFactory(key="logo")
        with pytest.raises(IntegrityError):
            SiteSettingFactory(key="logo")

    def test_str_returns_key(self):
        s = SiteSettingFactory(key="organigramme")
        assert str(s) == "organigramme"


@pytest.mark.django_db
class TestTeamMember:
    def test_full_name(self):
        m = TeamMemberFactory(first_name="Moussa", last_name="Ibrahim")
        assert m.full_name == "Moussa Ibrahim"

    def test_initials(self):
        m = TeamMemberFactory(first_name="Moussa", last_name="Ibrahim")
        assert m.initials == "MI"

    def test_str(self):
        m = TeamMemberFactory(first_name="Moussa", last_name="Ibrahim")
        assert str(m) == "Moussa Ibrahim"

    def test_ordering(self):
        TeamMember.objects.all().delete()
        dept_a = DepartmentFactory(order=0)
        dept_b = DepartmentFactory(order=1)
        m2 = TeamMemberFactory(department=dept_b, order=1, last_name="B")
        m1 = TeamMemberFactory(department=dept_a, order=0, last_name="A")
        m3 = TeamMemberFactory(department=dept_b, order=0, last_name="A")
        result = list(TeamMember.objects.all())
        assert result == [m1, m3, m2]

    def test_photo_resize_large_image(self, tmp_path, settings):
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image as PILImage

        img = PILImage.new("RGB", (300, 300), color="red")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        photo = SimpleUploadedFile("big.png", buf.read(), content_type="image/png")

        settings.MEDIA_ROOT = str(tmp_path)
        m = TeamMemberFactory(photo=photo)
        opened = PILImage.open(m.photo.path)
        assert opened.width <= 100
        assert opened.height <= 100

    def test_no_photo_no_error(self):
        m = TeamMemberFactory(photo="")
        assert str(m)
