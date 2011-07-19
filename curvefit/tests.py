# Tests for curvefit app

import os
import xlrd, xlwt

from django.test import TestCase

from settings import MEDIA_ROOT, PROJECT_PATH
from curvefit.views import *

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
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.xls')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i*i for i in range(15)])
        self.assertEqual(fit.msg, '')
    
    def test_read_csv_files(self):
        """
        Test that csv files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.csv")
        csv = open(filename, "w")
        for i in range(15):
            csv.write("%d,%d\n" % (i, i*i))
        csv.close()
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.csv')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i*i for i in range(15)])
        self.assertEqual(fit.msg, '')
    
    def test_read_txt_files(self):
        """
        Test that txt files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.txt")
        txt = open(filename, "w")
        for i in range(15):
            txt.write("%d\t%d\n" % (i, i*i))
        txt.close()
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.txt')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i*i for i in range(15)])
        self.assertEqual(fit.msg, '')
    
    def test_bad_txt_file(self):
        """
        Test that imporperly formated txt files are handled sanely
        """
        filename = os.path.join(MEDIA_ROOT, "test.txt")
        txt = open(filename, "w")
        for i in range(15):
            txt.write("%d,%d\n" % (i, i*i))
        txt.close()
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.txt')
        self.assertEqual(list(map(int, fit.x)), [])
        self.assertEqual(list(map(int, fit.y)), [])
        self.assertEqual(fit.msg, 'Cannot read data from input file.')

    
class CurveFitTest(TestCase):
    """
    Test that the curvefit functions return the expected values.
    """
    def test_boltzmann_model(self):
        """
        Test that the boltzman model returns input params for an ideal curve
        """
        param = [0.0012, 0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = np.array([10**xi for xi in x])
        y = param[0] + ((param[1] - param[0]) /
                            (1 + np.exp((param[2] - x) / param[3])))
        fit = CurveFit('dummy', 'boltzmann', [1.0, 1.0, 1.0, 1.0])
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = " ".join(map(lambda x: "%.4f" % x, param))
        vals_to_str = " ".join(map(lambda x: "%.4f" % x, vals))
        self.assertEqual(vals_to_str, param_to_str)
    
    def test_expdecay_model(self):
        """
        Test that the expdecay model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        x = np.arange(1, 40, 1)
        y = param[0] + param[1] * np.exp(-param[2] * x)
        fit = CurveFit('dummy', 'expdecay', [1.0, 1.0, 1.0])
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = " ".join(map(lambda x: "%.4f" % x, param))
        vals_to_str = " ".join(map(lambda x: "%.4f" % x, vals))
        self.assertEqual(vals_to_str, param_to_str)
        
    def test_hill_model(self):
        """
        Test that the hill model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = np.array([10**xi for xi in x])
        y = param[0] / (1 + (param[1]/x)**param[2])
        fit = CurveFit('dummy', 'hill', [1.0, 1.0, 1.0])
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = " ".join(map(lambda x: "%.4f" % x, param))
        vals_to_str = " ".join(map(lambda x: "%.4f" % x, vals))
        self.assertEqual(vals_to_str, param_to_str)
        
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
        fit = CurveFit('dummy', 'ic50', [1.0, 1.0, 1.0])
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = " ".join(map(lambda x: "%.4f" % x, param))
        vals_to_str = " ".join(map(lambda x: "%.4f" % x, vals))
        self.assertEqual(vals_to_str, param_to_str)
        
    def test_mm_model(self):
        """
        Test that the ic50 model returns input params for an ideal curve
        """
        param = [9.563, 0.6257]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = np.array([10**xi for xi in x])
        y = (param[0] * x) / (param[1] + x)
        fit = CurveFit('dummy', 'mm', [1.0, 1.0])
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        # round values to minimize floating point differences
        param_to_str = " ".join(map(lambda x: "%.4f" % x, param))
        vals_to_str = " ".join(map(lambda x: "%.4f" % x, vals))
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
        y = 1 - (param[0]/(1 + (param[1]/x) ** param[2]))
        fit = CurveFit('dummy','ic50', param)
        fit.x = x
        fit.y = y
        iters, vals = fit.levenberg_marquardt()
        self.assertEqual(iters, 0)

class CurvefitFormTest(TestCase):
    """
    Test the form webpage.
    """
    def test_response_is_200(self):
        response = self.client.get('/curvefit/')
        self.assertEqual(response.status_code, 200)
    def test_page_has_title(self):
        response = self.client.get('/curvefit/')
        self.assertEqual(
            "<title>CurveFit | Curve Fit</title>" in response.content, True
        )
    def test_page_has_curvefit_options(self):
        MODEL_CHOICES = (
            ('boltzmann', 'Boltzmann sigmoid'),
            ('expdecay', 'Exponential Decay'),
            ('gaussian', 'Gaussian function'),
            ('hill', 'Hill plot'),
            ('ic50', 'Dose Response (ic50)'),
            ('mm', 'Michaelis-Menten'),
            ('modsin', 'Modified sine wave'),
        )
        response = self.client.get('/curvefit/')
        for i in MODEL_CHOICES:
            opt = "<option value=\"%s\">%s</option>" % (i[0], i[1])
            self.assertEqual(opt in response.content, True)
            
class CurvefitSuccessTest(TestCase):
    """
    Test the Success page
    """
    def setUp(self):
        """
        Create files for form.
        """
        # Fake data...
        param = [0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = [10**xi for xi in x]
        # create files...
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        csvfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.csv'))
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet 1')
        csv = open(csvfile, "w")
        txt = open(txtfile, "w")
        # write data to files...
        for i, xi in enumerate(x):
            yi = 1 - (param[0]/(1 + (param[1]/xi) ** param[2]))
            sheet.write(i, 0, xi)
            sheet.write(i, 1, yi)
            csv.write("%f,%f\n" % (xi, yi))
            txt.write("%f\t%f\n" % (xi, yi))
        wbk.save(wbfile)
        csv.close()
        txt.close()
        
    def test_curvefit_success_is_200(self):
        """
        Success returns a webpage
        """
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(wbfile, "rb")
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        
    def test_curvefit_success_title(self):
        """
        Success produces the expected content (title).
        """
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(wbfile, "rb")
            }, follow=True
        )
        self.assertEqual(
            "<title>CurveFit | Fit Results</title>" in response.content, True
        )
    
    def test_curvefit_success_fit_params(self):
        """
        Success produces the expected content (parameters).
        """
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(wbfile, "rb")
            }, follow=True
        )
        self.assertEqual(
            "<td>0.9563</td>" in response.content, True
        )
        self.assertEqual(
            "<td>0.1221</td>" in response.content, True
        )
        self.assertEqual(
            "<td>1.7532</td>" in response.content, True
        )
        
    def test_curvefit_success_csv_files_work_too(self):
        """
        csv files are processed successfully.
        """
        csvfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.csv'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(csvfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            "<td>0.9563</td>" in response.content, True
        )
        self.assertEqual(
            "<td>0.1221</td>" in response.content, True
        )
        self.assertEqual(
            "<td>1.7532</td>" in response.content, True
        )
        
    def test_curvefit_success_txt_files_work_too(self):
        """
        txt files are processed successfully.
        """
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(txtfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            "<td>0.9563</td>" in response.content, True
        )
        self.assertEqual(
            "<td>0.1221</td>" in response.content, True
        )
        self.assertEqual(
            "<td>1.7532</td>" in response.content, True
        )

    def test_axis_labels_are_not_required(self):
        """
        txt files are processed successfully.
        """
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "",
                'y_label': "",
                'infile': open(txtfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            "<td>0.9563</td>" in response.content, True
        )
        self.assertEqual(
            "<td>0.1221</td>" in response.content, True
        )
        self.assertEqual(
            "<td>1.7532</td>" in response.content, True
        )
class CurveFitFailTest(TestCase):
    """
    Test that fails are handled well.
    """
    def setUp(self):
        """
        Create files for form.
        """
        # Fake data...
        param = [0.9563, 0.1221, 1.7532]
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin)/25)
        x = [10**xi for xi in x]
        # create files...
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        okwbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 
                                                           'oktest.xls'))
        csvfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.csv'))
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        wbk = xlwt.Workbook()
        okwbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet 1')
        oksheet = okwbk.add_sheet('sheet 1')
        csv = open(csvfile, "w")
        txt = open(txtfile, "w")
        # write data to files...
        for i, xi in enumerate(x):
            yi = 1 - (param[0]/(1 + (param[1]/xi) ** param[2]))
            sheet.write(i, 1, xi)
            sheet.write(i, 2, yi)
            oksheet.write(i, 0, xi)
            oksheet.write(i, 1, yi)
            csv.write(",%f,%f\n" % (xi, yi))
            txt.write("%f,%f\n" % (xi, yi))
        wbk.save(wbfile)
        okwbk.save(okwbfile)
        csv.close()
        txt.close()

    def test_bad_txt_file_gives_200(self):
        """
        Bad input should still return a page.
        """
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(txtfile, "rU")
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_bad_txt_file_gives_form_page(self):
        """
        Bad input should return form page.
        """
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(txtfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            "<title>CurveFit | Curve Fit</title>" in response.content, True
        )
    
    def test_bad_txt_file_gives_msg(self):
        txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(txtfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            '<p class="errorlist">Cannot read data from input file.</p>' \
            in response.content, True
        )

    def test_bad_csv_file_gives_msg(self):
        csvfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.csv'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "x axis",
                'y_label': "y axis",
                'infile': open(csvfile, "rU")
            }, follow=True
        )
        self.assertEqual(
            '<p class="errorlist">Cannot read data. Empty input.</p>' \
            in response.content, True
        )

    def test_bad_xls_file_gives_msg(self):
        xlsfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "x axis",
                'y_label': "y axis",
                'infile': open(xlsfile, "rb")
            }, follow=True
        )
        self.assertEqual(
            '<p class="errorlist">Cannot read data. Empty input.</p>' \
            in response.content, True
        )

    def test_bad_input_non_float_guess(self):
        okxlsfile = os.path.join(PROJECT_PATH, os.path.join('tests', 
                                                            'oktest.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 'one',
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "x axis",
                'y_label': "y axis",
                'infile': open(okxlsfile, "rb")
            }, follow=True
        )
        self.assertEqual(
            '<ul class="errorlist"><li>Enter a number.</li>' \
            in response.content, True
        )

    def test_no_input_file(self):
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': 1.0,
                'm2': 1.0,
                'm3': 1.0,
                'm4': 1.0,
                'x_label': "x axis",
                'y_label': "y axis",
            }, follow=True
        )
        self.assertEqual(
            '<ul class="errorlist"><li>This field is required.</li></ul>' \
            in response.content, True
        )

    def test_curvefit_fails_without_guess(self):
        okxlsfile = os.path.join(PROJECT_PATH, os.path.join('tests', 
                                                            'oktest.xls'))
        response = self.client.post('/curvefit/',
            {
                'model': 'ic50',
                'm1': '',
                'm2': '',
                'm3': '',
                'm4': '',
                'x_label': "y axis",
                'y_label': "x axis",
                'infile': open(okxlsfile, "rb")
            }, follow=True
        )
        self.assertEqual(
            '<ul class="errorlist"><li>This field is required.</li></ul>' \
            in response.content, True
        )


