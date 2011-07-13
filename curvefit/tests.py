# Tests for curvefit app

import os
import xlrd, xlwt

from django.test import TestCase

from settings import MEDIA_ROOT
from curvefit.file_handler import file_handler
from curvefit.functions import *

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
        self.assertEqual(m, '')
        # clean up
        os.remove(filename)
    
    def test_read_csv_files(self):
        """
        Test that csv files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.csv")
        csv = open(filename, "w")
        for i in range(15):
            csv.write("%d,%d\n" % (i, i*i))
        csv.close()
        x, y, m = file_handler(filename, '.csv')
        self.assertEqual(x, range(15))
        self.assertEqual(y, [i*i for i in range(15)])
        self.assertEqual(m, '')
        os.remove(filename)
    
    def test_read_txt_files(self):
        """
        Test that txt files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.txt")
        csv = open(filename, "w")
        for i in range(15):
            csv.write("%d\t%d\n" % (i, i*i))
        csv.close()
        x, y, m = file_handler(filename, '.txt')
        self.assertEqual(x, range(15))
        self.assertEqual(y, [i*i for i in range(15)])
        self.assertEqual(m, '')
        os.remove(filename)
    
    # Add tests for unexpected formats
    
class CurveFitTest(TestCase):
    """
    Test that the curvefit functions return the expected values.
    """
    def test_ic50_model(self):
        """
        Test that the ic50 model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = np.array([10**xi for xi in x])
        y = 1 - (param[0]/
                 (1 + (param[1]/x) ** param[2]))
        fit = CurveFit('ic50', [1.0, 1.0, 1.0], x, y)
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = "%.4f, %.4f, %.4f" % (param[0], param[1], param[2])
        vals_to_str = "%.4f, %.4f, %.4f" % (vals[0], vals[1], vals[2])
        self.assertEqual(vals_to_str, param_to_str)
    
    def test_perfect_guess(self):
        """
        A perfect guess should not iterate
        """
        param = [0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = np.array([10**xi for xi in x])
        y = 1 - (param[0]/
                 (1 + (param[1]/x) ** param[2]))
        fit = CurveFit('ic50', param, x, y)
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        self.assertEqual(iters, 0)
