import sys
import os
import pandas as pd
import json
import NGSF_version

try:
    configfile = os.environ["NGSFCONFIG"]
except KeyError:
    configfile = os.path.join(NGSF_version.CONFIG_DIR, "parameters.json")
with open(configfile) as config_file:
    ngsf_cfg = json.load(config_file)

spec_filename = sys.argv[1]
z = sys.argv[2]

to_fit_dir = ngsf_cfg['spectra_dir']
z_fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results_z/'
fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results/'

cmd_no_z = 'python run.py ' + str(to_fit_dir) + str(spec_filename) + ' ' + '100'

os.system(cmd_no_z)

if float(z) != 100:
    cmd_z = 'python run.py ' + str(to_fit_dir) + str(spec_filename) + ' ' + str(z)
    os.system(cmd_z)

elif float(z) == 100:
    spec = str(spec_filename)
    name = spec.split('.')[0]
    fitted_csv = fit_dir + name + '.csv'
    df = pd.read_csv(fitted_csv)
    fit_z = df['Z'][0]
    cmd_z = 'python run.py ' + str(to_fit_dir) + str(spec_filename) + ' ' + str(fit_z)
    os.system(cmd_z)
        
    


