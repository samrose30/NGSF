import json, simplejson
import os
import requests
import numpy as np
import base64
global TOKEN, BASEURL
GETTOKEN = 'c4b36f88-ebb7-4b74-89f2-519ffb637236'      # Fritz API Key, retrieves from info file
BASEURL = 'https://fritz.science/'


def api(method, endpoint, data=None, params=None, timeout=10):
    ''' Info : Basic API query, takes input the method (eg. GET, POST, etc.), the endpoint (i.e. API url)
               and additional data for filtering
        Returns : response in json format
        CAUTION! : If the query doesn't go through, try putting the 'data' input in 'data' or 'params'
                    argument in requests.request call
    '''

    headers = {'Authorization': f'token {GETTOKEN}'}

    while True:
        try:
            response = requests.request(method, endpoint, json=data, headers=headers, params=params, timeout=timeout)
            re_dict = response.json()

            if '429 Too Many Requests' in response.text:
                continue

            if json.loads(response.text)['status'] == 'error' and json.loads(response.text)['message'] == 'System provisioning':
                print('System provisioning...')
                time.sleep(10)
                continue

            return re_dict
        except requests.exceptions.Timeout:
            print('Timeout Exception, restarting...')
            continue
        except (json.decoder.JSONDecodeError, simplejson.errors.JSONDecodeError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            #print('JSON Decode Error, restarting...')
            continue





def get_redshift(ztfname, return_err=False):

    ''' Info : Query the redshift for any source
        Input : ZTFname
        Returns : redshift
    '''

    url = BASEURL+'api/sources/'+ztfname
    response = api('GET',url)

    redshift = response['data']['redshift']
    redshift_err = response['data']['redshift_error']

    if return_err == False:
        return redshift
    else:
        return redshift, redshift_err


def post_comment(ztfname, text, attach=None, attach_name=None, RCF_only=False):

    ''' Info : Posts a comment on transient's Fritz page
        Input : ZTFname, text
        Returns : API response
    '''

    if RCF_only == False:
        data = {
                "text": text, 
               }
    elif RCF_only == True:
        data = {
                "text": text,
                "group_ids": [41, 280, 1621],  # RCF, RCFDeepSurvey, RCFDeepPartnership 
               }

    if attach != None:
        with open(attach, "rb") as img_file:
            at_str = base64.b64encode(img_file.read()).decode('utf-8')

        data['attachment'] = {'body': at_str, 'name': attach_name}

    url = BASEURL+'api/sources/'+ztfname+'/comments'

    response = api('POST', url, data=data)

    return response

def get_spectrum_api(spectrum_id):
    ''' Info : Query all spectra corresponding to a source, takes input ZTF name
        Returns : list of spectrum jsons
    '''
    url = BASEURL+'api/spectrum/'+str(spectrum_id)
    response = api('GET',url)
    return response


def write_ascii_file_from_specid(specid, path):

    ''' Info : Generates ASCII file with data from selected Fritz spectrum
        Input : spectrum ID on Fritz, path
        Returns : spectrum_name (name of file), specid, ztfname
    '''

    a = get_spectrum_api(specid)

    inst = (a['data']['instrument_name'])
    ztfname = (a['data']["obj_id"])

    #print(inst)
    #print(a['data'].keys())

    if inst == 'SEDM':

        header = (a['data']['altdata'])


        s = (ztfname+'_'+str(header['OBSDATE'])+'_'+str(inst)+'.ascii')

        with open(path + s,'w') as f:
            f.write(a['data']['original_file_string'])
        f.close()

        #print (s,'\n')
        spectrum_name = s


    elif inst == 'SPRAT':

        header = (a['data']['altdata'])

        if len(header) > 0:
            try:
                s = (ztfname+'_'+str(header['OBSDATE'].split('T')[0])+'_'+str(inst)+'.ascii')
            except KeyError:
                s = (ztfname+'_'+str(a['data']['observed_at'].split('T')[0])+'_'+str(a['data']['instrument_name'])+'.ascii')

        else:
            s = (ztfname+'_'+str(a['data']['observed_at'].split('T')[0])+'_'+str(a['data']['instrument_name'])+'.ascii')


        with open(path + s,'w') as f:
            f.write(a['data']['original_file_string'])
        f.close()

        #print (s,'\n')
        spectrum_name = s


    elif inst == 'ALFOSC':

        OBSDATE = a['data']['observed_at'].split('T')[0]


        s = (ztfname+'_'+str(OBSDATE)+'_'+str(inst)+'.ascii')

        with open(path + s,'w') as f:
            f.write(a['data']['original_file_string'])
        f.close()

        #print (s,'\n')
        spectrum_name = s

    elif inst == 'KAST':

        OBSDATE = a['data']['observed_at'].split('T')[0]


        s = (ztfname+'_'+str(OBSDATE)+'_'+str(inst)+'.ascii')

        with open(path + s,'w') as f:
            f.write(a['data']['original_file_string'])
        f.close()

        #print (s,'\n')
        spectrum_name = s


    elif inst == 'DBSP':

        wav = (a['data']['wavelengths'])
        flux = (a['data']['fluxes'])
        err = (a['data']['errors'])

        OBSDATE = a['data']['observed_at'].split('T')[0]

        # get rid of NaNs
        idx_nans = np.where(~np.isfinite(np.array(flux, dtype=float)))[0]
        idx_nans = np.flip(idx_nans) #have to move from end to beginning to avoid messing up index
        for i in idx_nans:
            del flux[i]
            del wav[i]
            try:
                del err[i]
            except:
                continue

        s = (ztfname+'_'+str(OBSDATE)+'_'+str(inst)+'.ascii')

        if err == None:

            with open(path + s,'w') as f:

                for i in range(len(wav)):
                    f.write(str(wav[i])+'\t'+str(flux[i])+'\n')
            f.close()

            #print (s,'\n')
            spectrum_name = s

        else:

            with open(path + s,'w') as f:

                for i in range(len(wav)):
                    f.write(str(wav[i])+'\t'+str(flux[i])+'\t'+str(err[i])+'\n')
            f.close()

            #print (s,'\n')
            spectrum_name = s


    elif inst == 'DIS':

        #obsdate = a['data']['original_file_string'].split('#')[6]
        #a,b = obsdate.split(' ', 1)
        #c,OBSDATE = b.split(' ', 1)
        #OBSDATE = OBSDATE.split('T')[0]

        obsdate = a['data']['observed_at']
        OBSDATE = obsdate.split('T')[0]


        path = path+'/data/'

        s = (ztfname+'_'+str(OBSDATE)+'_'+str(inst)+'.ascii')

        a = get_spectrum_api(specid)

        with open(path + s,'w') as f:
            f.write(a['data']['original_file_string'])
        f.close()

        #print (s,'\n')
        spectrum_name = s


    elif inst == 'LRIS' or inst == 'NIRES' or inst == 'GMOS_GS' or inst == 'FLOYDS' or inst == 'Deveny+LMI':

        wav = (a['data']['wavelengths'])
        flux = (a['data']['fluxes'])
        err = (a['data']['errors'])

        OBSDATE = a['data']['observed_at'].split('T')[0]

        s = (ztfname+'_'+str(OBSDATE)+'_'+str(inst)+'.ascii')

        if err == None:

            with open(path + s,'w') as f:

                for i in range(len(wav)):
                    f.write(str(wav[i])+'\t'+str(flux[i])+'\n')
            f.close()

            #print (s,'\n')
            spectrum_name = s

        else:

            with open(path + s,'w') as f:

                for i in range(len(wav)):
                    f.write(str(wav[i])+'\t'+str(flux[i])+'\t'+str(err[i])+'\n')
            f.close()

            #print (s,'\n')
            spectrum_name = s


    elif inst == 'EFOSC2':

        spectrum_name = 'TNS_spectrum'

    else:
        spectrum_name = None

    return spectrum_name, specid, ztfname
