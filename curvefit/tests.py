# Tests for curvefit app

import os
import xlrd, xlwt

from django.test import TestCase

from settings import MEDIA_ROOT, PROJECT_PATH
from curvefit.views import *


def write_file_data(filename, sep=None):
    if sep:
        f = open(filename, "w")
        data = ["%d%s%d\n" % (i, sep, i * i) for i in xrange(15)]
        f.writelines(data)
        f.close()
    else:
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet 1')
        for i in range(15):
            sheet.write(i, 0, i)
            sheet.write(i, 1, i * i)
        wbk.save(filename)


def file_setup():
    # Fake data...
    param = [0.9563, 0.1221, 1.7532]
    xmax = np.log10(150)
    xmin = np.log10(0.001)
    x = np.arange(xmin, xmax, (xmax - xmin) / 25)
    x = [10 ** xi for xi in x]
    # create files...
    wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.xls'))
    csvfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.csv'))
    txtfile = os.path.join(PROJECT_PATH, os.path.join('tests', 'test.txt'))
    badwbfile = os.path.join(PROJECT_PATH,
                             os.path.join('tests', 'badtest.xls'))
    badcsvfile = os.path.join(PROJECT_PATH,
                              os.path.join('tests', 'badtest.csv'))
    badtxtfile = os.path.join(PROJECT_PATH,
                              os.path.join('tests', 'badtest.txt'))
    wbk = xlwt.Workbook()
    badwbk = xlwt.Workbook()
    sheet = wbk.add_sheet('sheet 1')
    badsheet = badwbk.add_sheet('sheet 1')
    csv = open(csvfile, "w")
    badcsv = open(badcsvfile, "w")
    txt = open(txtfile, "w")
    badtxt = open(badtxtfile, "w")
    # write data to files...
    for i, xi in enumerate(x):
        yi = 1 - (param[0] / (1 + (param[1] / xi) ** param[2]))
        sheet.write(i, 0, xi)
        sheet.write(i, 1, yi)
        badsheet.write(i, 1, xi)
        badsheet.write(i, 2, yi)
        csv.write("%f,%f\n" % (xi, yi))
        badcsv.write(",%f,%f\n" % (xi, yi))
        txt.write("%f\t%f\n" % (xi, yi))
        badtxt.write("%f,%f\n" % (xi, yi))
    wbk.save(wbfile)
    badwbk.save(badwbfile)
    csv.close()
    badcsv.close()
    txt.close()
    badtxt.close()


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
        write_file_data(filename)
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.xls')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i * i for i in range(15)])
        self.assertEqual(fit.msg, '')

    def test_read_csv_files(self):
        """
        Test that csv files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.csv")
        write_file_data(filename, sep=",")
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.csv')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i * i for i in range(15)])
        self.assertEqual(fit.msg, '')

    def test_read_txt_files(self):
        """
        Test that txt files are read and data is correct.
        """
        filename = os.path.join(MEDIA_ROOT, "test.txt")
        write_file_data(filename, sep="\t")
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.txt')
        self.assertEqual(list(map(int, fit.x)), range(15))
        self.assertEqual(list(map(int, fit.y)), [i * i for i in range(15)])
        self.assertEqual(fit.msg, '')

    def test_bad_txt_file(self):
        """
        Test that imporperly formated txt files are handled sanely
        """
        filename = os.path.join(MEDIA_ROOT, "test.txt")
        write_file_data(filename, sep=",")
        fit = CurveFit(filename, 'ic50', [1.0, 1.0, 1.0])
        fit.file_handler('.txt')
        self.assertEqual(list(map(int, fit.x)), [])
        self.assertEqual(list(map(int, fit.y)), [])
        self.assertEqual(fit.msg, 'Cannot read data from input file.')


class CurveFitTest(TestCase):
    """
    Test that the curvefit functions return the expected values.
    """
    def run_levenberg_marquardt(self, model, param, yfunc):
        if model in [
                'var0 + ((var1 - var0) / (1 + exp((var2 - x) / var3)))',
                'var0 / (1 + (var1 / x)** var2)',
                '1 - (var0 / (1 + (var1 / x) ** var2))'
        ]:
            xmax = np.log10(150)
            xmin = np.log10(0.001)
            x = np.arange(xmin, xmax, (xmax - xmin) / 25)
            x = np.array([10 ** xi for xi in x])
        else:
            x = np.arange(1, 40, 1)
        y = yfunc(param, x)
        fit = CurveFit('dummy', model, [1.0] * len(param))
        fit.x = x
        fit.y = y
        return fit.levenberg_marquardt()

    def test_boltzmann_model(self):
        """
        Test that the boltzman model returns input params for an ideal curve
        """
        param = [0.0012, 0.9563, 0.1221, 1.7532]
        model = 'var0 + ((var1 - var0) / (1 + exp((var2 - x) / var3)))'
        y = lambda param, x: param[0] + (
            (param[1] - param[0]) / (1 + np.exp((param[2] - x) / param[3]))
        )
        iters, vals = self.run_levenberg_marquardt(model, param, y)
        self.assertTrue(np.allclose(vals, param))

    def test_expdecay_model(self):
        """
        Test that the expdecay model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        model = 'var0 + var1 * exp(-var2 * x)'
        y = lambda param, x: param[0] + param[1] * np.exp(-param[2] * x)
        iters, vals = self.run_levenberg_marquardt(model, param, y)
        self.assertTrue(np.allclose(vals, param))

    def test_hill_model(self):
        """
        Test that the hill model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        model = 'var0 / (1 + (var1 / x)** var2)'
        y = lambda param, x: param[0] / (1 + (param[1] / x) ** param[2])
        iters, vals = self.run_levenberg_marquardt(model, param, y)
        self.assertTrue(np.allclose(vals, param))

    def test_ic50_model(self):
        """
        Test that the ic50 model returns input params for an ideal curve
        """
        param = [0.9563, 0.1221, 1.7532]
        model = '1 - (var0 / (1 + (var1 / x) ** var2))'
        y = lambda param, x: 1 - (
            param[0] / (1 + (param[1] / x) ** param[2])
        )
        iters, vals = self.run_levenberg_marquardt(model, param, y)
        self.assertTrue(np.allclose(vals, param))

    def test_mm_model(self):
        """
        Test that the ic50 model returns input params for an ideal curve
        """
        param = [9.563, 0.6257]
        model = '(var0 * x) / (var1 + x)'
        y = lambda param, x: (param[0] * x) / (param[1] + x)
        iters, vals = self.run_levenberg_marquardt(model, param, y)
        self.assertTrue(np.allclose(vals, param))

    def test_perfect_guess(self):
        """
        A perfect guess should not iterate
        """
        param = [0.9563, 0.1221, 1.7532]
        model = '1 - (var0 / (1 + (var1 / x) ** var2))'
        xmax = np.log10(150)
        xmin = np.log10(0.001)
        x = np.arange(xmin, xmax, (xmax - xmin) / 25)
        x = np.array([10 ** xi for xi in x])
        y = 1 - (param[0] / (1 + (param[1] / x) ** param[2]))
        fit = CurveFit('dummy', model, param)
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
        self.assertIn("<title>CurveFit | Curve Fit</title>", response.content)

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
            self.assertIn(opt, response.content)


class CurvefitSuccessTest(TestCase):
    """
    Test the Success page
    """
    def setUp(self):
        """
        Create files for form.
        """
        # Fake data...
        file_setup()

    def tearDown(self):
        for f in os.listdir(MEDIA_ROOT):
            os.remove(os.path.join(MEDIA_ROOT, f))

    def setup_response(self,
                       filename,
                       model='1 - (var0 / (1 + (var1 / x) ** var2))',
                       var=1.0,
                       label='a label'):
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', filename))
        if filename[-4::] == ".xls":
            f = open(wbfile, "rb")
        else:
            f = open(wbfile, "rU")
        response = self.client.post(
            '/curvefit/',
            {
                'model': model,
                'm1': var,
                'm2': var,
                'm3': var,
                'm4': var,
                'x_label': label,
                'y_label': label,
                'infile': f
            }, follow=True
        )
        return response

    def test_curvefit_success_is_200(self):
        """
        Success returns a webpage
        """
        response = self.setup_response("test.xls")
        self.assertEqual(response.status_code, 200)

    def test_curvefit_success_title(self):
        """
        Success produces the expected content (title).
        """
        response = self.setup_response("test.xls")
        self.assertIn("<title>CurveFit | Fit Results</title>",
                      response.content)

    def test_curvefit_success_fit_params(self):
        """
        Success produces the expected content (parameters).
        """
        response = self.setup_response("test.xls")
        self.assertIn("<td>0.9563</td>", response.content)
        self.assertIn("<td>0.1221</td>", response.content)
        self.assertIn("<td>1.7532</td>", response.content)

    def test_curvefit_success_csv_files_work_too(self):
        """
        csv files are processed successfully.
        """
        response = self.setup_response("test.csv")
        self.assertIn("<td>0.9563</td>", response.content)
        self.assertIn("<td>0.1221</td>", response.content)
        self.assertIn("<td>1.7532</td>", response.content)

    def test_curvefit_success_txt_files_work_too(self):
        """
        txt files are processed successfully.
        """
        response = self.setup_response("test.txt")
        self.assertIn("<td>0.9563</td>", response.content)
        self.assertIn("<td>0.1221</td>", response.content)
        self.assertIn("<td>1.7532</td>", response.content)

    def test_axis_labels_are_not_required(self):
        """
        Labels for the graph shouldn't be required'.
        """
        response = self.setup_response("test.txt", label="")
        self.assertIn("<td>0.9563</td>", response.content)
        self.assertIn("<td>0.1221</td>", response.content)
        self.assertIn("<td>1.7532</td>", response.content)


class CurveFitFailTest(TestCase):
    """
    Test that fails are handled well.
    """
    def setUp(self):
        """
        Create files for form.
        """
        # Fake data...
        file_setup()

    def tearDown(self):
        for f in os.listdir(MEDIA_ROOT):
            os.remove(os.path.join(MEDIA_ROOT, f))

    def setup_response(self,
                       filename,
                       model='1 - (var0 / (1 + (var1 / x) ** var2))',
                       var=1.0,
                       label='a label'):
        wbfile = os.path.join(PROJECT_PATH, os.path.join('tests', filename))
        if filename[-4::] == ".xls":
            f = open(wbfile, "rb")
        else:
            f = open(wbfile, "rU")
        response = self.client.post(
            '/curvefit/',
            {
                'model': model,
                'm1': var,
                'm2': var,
                'm3': var,
                'm4': var,
                'x_label': label,
                'y_label': label,
                'infile': f
            }, follow=True
        )
        return response

    def test_bad_txt_file_gives_200(self):
        """
        Bad input should still return a page.
        """
        response = self.setup_response('badtest.txt')
        self.assertEqual(response.status_code, 200)

    def test_bad_txt_file_gives_form_page(self):
        """
        Bad input should return form page.
        """
        response = self.setup_response('badtest.txt')
        self.assertIn("<title>CurveFit | Curve Fit</title>", response.content)

    def test_bad_txt_file_gives_msg(self):
        """
        Bad input should return a message
        """
        response = self.setup_response('badtest.txt')
        self.assertIn(
            '<p class="errorlist">Cannot read data from input file.</p>',
            response.content)

    def test_bad_csv_file_gives_msg(self):
        """
        A bad csv file should give a message too.
        """
        response = self.setup_response('badtest.csv')
        self.assertIn(
            '<p class="errorlist">Cannot read data. Empty input.</p>',
            response.content)

    def test_bad_xls_file_gives_msg(self):
        """
        A bad xls file should give a message too.
        """
        response = self.setup_response('badtest.xls')
        self.assertIn(
            '<p class="errorlist">Cannot read data. Empty input.</p>',
            response.content)

    def test_bad_input_non_float_guess(self):
        """
        A non-float variable should give a message.
        """
        response = self.setup_response('test.xls', var="one")
        self.assertIn('<ul class="errorlist"><li>Enter a number.</li>',
                      response.content)

    def test_no_input_file(self):
        """
        Not providing a file should give a message.
        """
        response = self.client.post(
            '/curvefit/',
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
        self.assertIn(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            response.content)

    def test_curvefit_fails_without_guess(self):
        """
        Not providing an initial guess should give a message
        """
        response = self.setup_response('test.xls', var="")
        self.assertIn(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            response.content)

    def test_curfit_fails_with_wrong_number_args(self):
        """
        Providing wrong number of args in model should give a message
        """
        response = self.setup_response('test.xls', model='log(x) + var0')
        self.assertIn(
            '<p class="errorlist">Supported models must have at least 2',
            response.content)
        response = self.setup_response(
            'test.xls',
            model='var2*log(var1*x) + var0*exp(var3*x / var4)')
        self.assertIn(
            '<p class="errorlist">Supported models must have at least 2',
            response.content)

    def test_bad_model(self):
        """
        A bad model should return a message.
        """
        response = self.setup_response('test.xls', model='print "hacked"; var0; var1')
        self.assertIn(
            '<p class="errorlist">There was an error in the model equation.</p>',
            response.content)
