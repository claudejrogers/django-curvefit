"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import xlrd, xlwt

from django.test import TestCase

from settings import MEDIA_ROOT
from curvefit.file_handler import file_handler


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class FileHandlerTest(TestCase):
    """
    Test that the file_handler function works and returns expected values.
    """
    def test_read_xls_files(self):
        """
        Test that xls files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.xls")
        # Write fake data to xls file.
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet 1')
        for i in range(15):
            sheet.write(i, 0, i)
            sheet.write(i, 1, i * i)
        wbk.save(filename)
        # test
        x, y, m = file_handler(filename, '.xls')
        self.assertEqual(x, range(15))
        self.assertEqual(y, [i*i for i in range(15)])
        # clean up
        os.remove(filename)
    def test_read_csv_files(self):
        
        
