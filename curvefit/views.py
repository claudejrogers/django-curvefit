import os
import matplotlib

matplotlib.use("Agg")

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf
from sympy.core.sympify import SympifyError

from curvefit.forms import CurvefitForm
from curvefit.functions import *
from curvefit.model_functions import find_nvars

def curvefit(request):
    if request.method == 'POST':
        form = CurvefitForm(request.POST, request.FILES)
        if form.is_valid():
            model = str(form.cleaned_data['model'])
            m1 = form.cleaned_data['m1']
            m2 = form.cleaned_data['m2']
            m3 = form.cleaned_data['m3']
            m4 = form.cleaned_data['m4']
            xlabel = form.cleaned_data['x_label']
            ylabel = form.cleaned_data['y_label']
            logscale = form.cleaned_data['logscale']
            infile = form.cleaned_data['infile']
            ext = os.path.splitext(infile.name)[1]
            if ext not in ['.txt', '.csv', '.xls']:
                msg = "%s is an unsupported file type." % ext
                form = CurvefitForm(request.POST)
                return render_to_response('curvefit/curvefitform.html', 
                                          {'form': form,
                                           'msg': msg},
                                context_instance=RequestContext(request))
            content = infile.read()
            filepath = os.path.join(MEDIA_ROOT, infile.name)
            if ext == '.xls':
                sf = open(filepath, "wb")
            else:
                sf = open(filepath, "w")
            sf.write(content)
            sf.close()
            
            nvars = find_nvars(model)
            if nvars == 4:
                var = np.array([m1, m2, m3, m4])
            elif nvars == 3:
                var = np.array([m1, m2, m3])
            elif nvars == 2:
                var = np.array([m1, m2])
            else:
                msg = "Supported models must have at least 2 \
                       and at most 4 independent variables!"
                form = CurvefitForm()
                return render_to_response('curvefit/curvefitform.html',
                                          {'form': form, 'msg': msg},
                                context_instance=RequestContext(request))
            plotname = "plot_" + random_key() + ".png"
            plotfile = os.path.join(MEDIA_ROOT, plotname)
            
            try:
                fit = CurveFit(filepath, model, var, logscale)
            except:
                msg = "There was an error in the model equation."
                form = CurvefitForm(request.POST)
                return render_to_response('curvefit/curvefitform.html',
                                          {'form': form, 'msg': msg},
                                context_instance=RequestContext(request))
            fit.file_handler(ext)
            if fit.msg:
                form = CurvefitForm(request.POST)
                return render_to_response('curvefit/curvefitform.html',
                                          {'form': form,
                                           'msg': fit.msg},
                                    context_instance=RequestContext(request))
            fit_var = fit.levenberg_marquardt()
            fit.plot(plotfile, xlabel, ylabel)
            
            filename = os.path.basename(filepath)
            
            c = {
                'filename': filename,
                'plotfile': plotname,
                'model': model,
                'k': fit_var[0],
                'var': fit_var[1],
            }    
            return render_to_response('curvefit/curvefitsuccess.html', c)
    else:
        form = CurvefitForm()
    return render_to_response('curvefit/curvefitform.html', {'form': form}, 
                              context_instance=RequestContext(request))

