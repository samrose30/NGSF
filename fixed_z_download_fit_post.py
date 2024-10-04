import os
from fritz_func import *
import sys
import json
import pandas as pd
import NGSF_version

try:
    configfile = os.environ["NGSFCONFIG"]
except KeyError:
    configfile = os.path.join(NGSF_version.CONFIG_DIR, "parameters.json")
with open(configfile) as config_file:
    ngsf_cfg = json.load(config_file)

to_fit_dir = ngsf_cfg['pkg_dir'] + 'spectra_to_fit/'
z_fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results_z/'
fit_dir = ngsf_cfg['pkg_dir'] + 'fit_results/'

if os.path.exists(to_fit_dir) == False: # if folder doesn't exist
    os.system('mkdir ' + to_fit_dir) # creates the folder

if os.path.exists(z_fit_dir) == False: # if folder doesn't exist
    os.system('mkdir ' + z_fit_dir) # creates the folder

if os.path.exists(fit_dir) == False: # if folder doesn't exist
    os.system('mkdir ' + fit_dir) # creates the folder

specid = sys.argv[1]

spec_filename, specid, ztfname = write_ascii_file_from_specid(specid, to_fit_dir)

z = get_redshift(ztfname)

if z == None:
    print('this object has no redshift on ztf, run download_fit_post.py instead')
    sys.exit()


if float(z) != 100:
    cmd_z = 'python run.py ' + str(to_fit_dir) + str(spec_filename) + ' ' + str(z)
    os.system(cmd_z)
    

images = []
prefix = spec_filename.split('.')[0]

for i in range(0, 3):
    fit_png_name = prefix + '_ngsf' + str(i) + '.png'
    fit_png_file_z = z_fit_dir + fit_png_name
    if os.path.exists(fit_png_file_z):
        images.append(fit_png_file_z)
    else:
        images.append('blank.png')

comb_fit_png_name = prefix + '_ngsf.png'
comb_fit_png_file = fit_dir + comb_fit_png_name
combine_images(columns=2, space=10, images=images, savepath=comb_fit_png_file)
    
text = 'Top 3 matches from superfit with redshift fixed to the Fritz value z = ' + str(z) + ' for ' + prefix + ' fritz specid ' + specid
response = post_comment(ztfname, text, comb_fit_png_file, comb_fit_png_name)
print(response)
