function get_equation(model_name) {
  var eqn_dict = {
    'boltzmann': 'var0 + ((var1 - var0)/(1 + exp((var2 - x)/var3)))',
    'expdecay': 'var0 + var1 * exp(-var2 * x)',
    'gaussian': 'var0 + var1 * exp(-(x - var2)^2 / var3^2)',
    'hill': 'var0 / (1 + (var1 / x)^var2)',
    'ic50': '1 - (var0 / (1 + (var1 / x)^var2))',
    'mm': '(var0 * x) / (var1 + x)',
    'modsin': 'var0 * sin(pi * (x - var1) / var2)'
  };
  return eqn_dict[model_name];
}
