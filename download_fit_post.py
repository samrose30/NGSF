import os
from fritz_func import *
import sys
import json
import NGSF_version

try:
    configfile = os.environ["NGSFCONFIG"]
except KeyError:
    configfile = os.path.join(NGSF_version.CONFIG_DIR, "parameters.json")
with open(configfile) as config_file:
    ngsf_cfg = json.load(config_file)

to_fit_dir = ngsf_cfg['spectra_dir']
z_fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results_z/'
fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results/'

specid = sys.argv[1]

spec_filename, specid, ztfname = write_ascii_file_from_specid(specid, to_fit_dir)

z = get_redshift(ztfname)

if z == None:
    z = 100

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
    z = fit_z


for i in range(0, 3):
    prefix = spec_filename.split('.')[0]
    fit_png_name = prefix + '_ngsf' + str(i) + '.png'
    fit_png_file = fit_dir + fit_png_name
    text = 'Top ' + str(i+1) + '/3 matches from superfit with redshift a free parameter'
    response = post_comment(ztfname, text, fit_png_file, fit_png_name)

for i in range(0, 3):
    prefix = spec_filename.split('.')[0]
    fit_png_name = prefix + '_ngsf' + str(i) + '.png'
    fit_png_file = z_fit_dir + fit_png_name
    text = 'Top ' + str(i+1) + '/3 matches from superfit with redshift set z=' + str(z)
    response = post_comment(ztfname, text, fit_png_file, fit_png_name) 
