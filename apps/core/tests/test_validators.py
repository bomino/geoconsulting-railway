import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import (
    MAX_FILE_SIZE,
    validate_document_file,
    validate_image_file,
)

VALID_HEADERS = {
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff\xe0",
    ".jpeg": b"\xff\xd8\xff\xe0",
    ".gif": b"GIF89a",
    ".pdf": b"%PDF-1.4",
    ".docx": b"PK\x03\x04",
    ".xlsx": b"PK\x03\x04",
    ".svg": b"<svg",
    ".webp": b"RIFF",
}


class TestImageValidator:
    @pytest.mark.parametrize("ext", [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"])
    def test_valid_extensions(self, ext):
        header = VALID_HEADERS[ext]
        f = SimpleUploadedFile(f"test{ext}", header, content_type="application/octet-stream")
        validate_image_file(f)

    def test_invalid_extension_raises(self):
        f = SimpleUploadedFile("test.exe", b"data", content_type="application/octet-stream")
        with pytest.raises(ValidationError):
            validate_image_file(f)


class TestDocumentValidator:
    @pytest.mark.parametrize("ext", [".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".gif"])
    def test_valid_extensions(self, ext):
        header = VALID_HEADERS[ext]
        f = SimpleUploadedFile(f"test{ext}", header, content_type="application/octet-stream")
        validate_document_file(f)

    def test_invalid_extension_raises(self):
        f = SimpleUploadedFile("test.py", b"data", content_type="application/octet-stream")
        with pytest.raises(ValidationError):
            validate_document_file(f)


class TestFileSizeLimit:
    def test_file_over_limit_raises(self):
        f = SimpleUploadedFile("big.png", b"\x89PNG", content_type="application/octet-stream")
        f.size = MAX_FILE_SIZE + 1
        with pytest.raises(ValidationError):
            validate_image_file(f)

    def test_file_at_limit_passes(self):
        f = SimpleUploadedFile("ok.png", b"\x89PNG\r\n\x1a\n", content_type="application/octet-stream")
        f.size = MAX_FILE_SIZE
        validate_image_file(f)


class TestMagicBytesValidation:
    def test_wrong_magic_bytes_raises(self):
        f = SimpleUploadedFile("fake.pdf", b"not a pdf", content_type="application/pdf")
        with pytest.raises(ValidationError, match="ne correspond pas"):
            validate_document_file(f)

    def test_correct_magic_bytes_passes(self):
        f = SimpleUploadedFile("real.pdf", b"%PDF-1.7 content", content_type="application/pdf")
        validate_document_file(f)
