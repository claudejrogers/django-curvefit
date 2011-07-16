import os
import matplotlib

matplotlib.use("Agg")

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf


from curvefit.forms import CurvefitForm
from curvefit.functions import *

def curvefit(request):
    if request.method == 'POST':
        form = CurvefitForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.cleaned_data['model']
            m1 = form.cleaned_data['m1']
            m2 = form.cleaned_data['m2']
            m3 = form.cleaned_data['m3']
            m4 = form.cleaned_data['m4']
            xlabel = form.cleaned_data['x_label']
            ylabel = form.cleaned_data['y_label']
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
            
            if model == "boltzmann" or model == "gaussian":
                var = np.array([m1, m2, m3, m4])
            elif (model == "expdecay" or model == "hill" or model == "ic50" 
                  or model == "modsin"):
                var = np.array([m1, m2, m3])
            elif model == "mm":
                var = np.array([m1, m2])
            
            plotname = "plot_" + random_key() + ".png"
            plotfile = os.path.join(MEDIA_ROOT, plotname)
            
            fit = CurveFit(filepath, model, var)
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
            
            # Get fancy name for model
            model_choices = (
                ('boltzmann', 'Boltzmann sigmoid'),
                ('expdecay', 'Exponential Decay'),
                ('gaussian', 'Gaussian function'),
                ('hill', 'Hill plot'),
                ('ic50', 'Dose Response (ic50)'),
                ('mm', 'Michaelis-Menten'),
                ('modsin', 'Modified sine wave'),
            )
            mchoices = [i for i, j in model_choices]
            this_model = model_choices[mchoices.index(model)][1]
            
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
