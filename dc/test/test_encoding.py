# -*- encoding: utf-8 -*-
# Warning: This file contains non-ASCII text. Please make sure that your editor
# is using the correct encoding before tampering around with this file.
from ..util import get_file_content
from contextlib import contextmanager
import os
import tempfile
import unittest


@contextmanager
def tempfile_with_content(content):
    file_obj = tempfile.NamedTemporaryFile(delete=False)
    file_obj.write(content)
    file_obj.close()
    yield file_obj
    os.unlink(file_obj.name)


class EncodingTestCase(unittest.TestCase):
    def test_utf_8(self):
        data = "Привет"
        with tempfile_with_content(data.encode("utf-8")) as tfile:
            read_data, encoding = get_file_content(tfile.name)
        self.assertEqual(read_data, data)
        self.assertEqual(encoding, "utf-8")

    def test_cp_1252(self):
        # CP-1252 can't encode Russian :(
        data = "förlåt"
        with tempfile_with_content(data.encode("windows-1252")) as tfile:
            read_data, encoding = get_file_content(tfile.name)
        self.assertEqual(read_data, data)
        self.assertEqual(encoding, "windows-1252")

    def test_ascii_fallback(self):
        # x81 is undefined in CP-1252
        # xe4 is ä in CP-1252 and should be removed
        data = b"\x81H\xe4llo"
        with tempfile_with_content(data) as tfile:
            read_data, encoding = get_file_content(tfile.name)
        self.assertEqual(read_data, "Hllo")
        self.assertEqual(encoding, "ascii")
