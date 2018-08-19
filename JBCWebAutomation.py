# -*- coding: utf-8 -*-
"""
Created on Sun Mar 09 19:24:55 2014

@author: yyu
"""

import os
import subprocess
import fnmatch
import shutil
from datetime import date
from ftplib import FTP
import ConfigParser

def GetToday():
	config = ConfigParser.RawConfigParser()
	config.read('JBCConfig.cfg')
	today = config.get("TD", "TD")
	print 'Getting today date'
	if today == 'auto': #generate with true today
		year = str(date.today().year)
		month = str(date.today().month)
		day = str(date.today().day)
		if len(month)==1:
			month = '0'+month
			day = str(date.today().day)
		if len(day)==1:
			day = '0'+day   
		today=year[2:5] + month + day
            
	return today
    
def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename
                
def ConvertSermonDOC2PDF(today_date, language_ID):                            
    config = ConfigParser.RawConfigParser()
    config.read('JBCConfig.cfg')
    swriter_path = config.get("swriter", "swriter_path")
    pdfdir_local = config.get("folders", "JBC_Digital_Recording")
    Secretary_path =config.get("folders", "Secretary")    
    
    year = str(date.today().year)
    in_file_path = Secretary_path + year +' Sermon Notes\\'
    
    if language_ID == 0: 
        lang = 'English'
        fn_pattern = today_date+'*.doc*'
    elif language_ID == 1:
        lang = 'Chinese'        
        fn_pattern = today_date+'*.doc*'
    elif language_ID == 2:
        lang = 'English' #save the combined into the English session
        fn_pattern = today_date+'*.doc*'
                
    outdir =os.path.abspath(pdfdir_local + lang + '_Digital_Recording\\'+ year + '\\Sermon_Notes\\')
    swriter = os.path.abspath(swriter_path + ' --headless --convert-to pdf --outdir')   
    fcnt=0
    print in_file_path + fn_pattern
  
    for doc_file_name in find_files(in_file_path, fn_pattern):
        print 'Converting '+  doc_file_name+ ' to PDF.......'
        in_file =  '\"' + doc_file_name + '\"'
        cmdline = swriter + ' ' + outdir + ' ' + in_file
        #print cmdline
        subprocess.call(cmdline) 
        fcnt+=1

    if fcnt==0:
        print 'ERROR: No input file to convert. Check date and directory'
    else:
        print 'Successfully converted file.'

def JBCFTPConnection():
    config = ConfigParser.RawConfigParser()
    config.read('FTPConfig.cfg')
    url = config.get("site", "url")
    port = config.get("site", "port")
    user = config.get("site", "user")
    pwd = config.get("site", "pwd")
    ftp = FTP()
    ftp.connect(url, port)     # connect to host, default port
    ftp.login(user, pwd)
    return ftp    

def upload(ftp, file):
    fn = os.path.split(file)
    ftp.storbinary("STOR " + fn[1], open(file, "rb"), 1024)
    print 'Validating uploaded file: '
    ftp.retrlines('LIST ' + fn[1])
    print 'Finish uploading this file.'

def copyfile(src, dst):
    print 'Copying file ' + src + ' to ' + dst
    shutil.copy(src, dst)
    print 'Finish copying'

def uploadJBCWeb(ftp, today_date, language_ID, file_type):
    config = ConfigParser.RawConfigParser()
    config.read('JBCConfig.cfg')    
    dir_local = config.get("folders", "JBC_Digital_Recording")
    dir_localCopy = config.get("folders", "JBC_Digital_Recording_COPY")
    pdf_remote = config.get("ftp", "pdf_remote")
    mp3_remote = config.get("ftp", "mp3_remote")    
    
    if language_ID == 0 or language_ID == 2: 
        lang = 'English'        
    elif language_ID ==1:
        lang = 'Chinese'        
        
    fn_pattern = today_date+'*.'+file_type
    year = str(date.today().year)
    
    if file_type=='pdf':
        localdir=os.path.abspath(dir_local + lang + '_Digital_Recording\\'+ year + '\\Sermon_Notes\\')
        localdircopy=os.path.abspath(dir_localCopy + lang + '_Digital_Recording\\'+ year + '\\Sermon_Notes\\')
        ftp.cwd(pdf_remote)
    else:
        localdir=os.path.abspath(dir_local + lang + '_Digital_Recording\\'+ year + '\\MP3\\')
        localdircopy=os.path.abspath(dir_localCopy + lang + '_Digital_Recording\\'+ year + '\\MP3\\')
        ftp.cwd(mp3_remote)
    
    fcnt = 0    
    for local_file_name in find_files(localdir, fn_pattern):
        copyfile(local_file_name, localdircopy)
        print 'Uploading '+  local_file_name+ ' to FTP server.....'            
        upload(ftp, local_file_name)   
        if file_type=='pdf':
                fn = os.path.split(local_file_name)[1]
                print 'Renaming pdf name from: ', fn, ' to ', fn[:6]+lang+'.pdf'
                ftp.rename(fn, fn[:6]+lang+'.pdf')			
        fcnt +=1
    
    if fcnt==0:
        print 'ERROR: No input file to upload. Check date and directory'
    else:
        print 'Successfully uploaded file.'
        

def download_file(ftp, remote_path, remote_fn, local_path, today):
    ftp.cwd(remote_path)
    local_fn = remote_fn[:-4]+today+'.xml'
    print 'Downloading ', remote_fn,'...'
    ftp.retrbinary("RETR " + remote_fn, open(local_path + local_fn, 'wb').write)
    return

def backup_podcast_xml(ftp, today):
    config = ConfigParser.RawConfigParser()
    config.read('JBCConfig.cfg')
    local_path = config.get("folders", "podcast_backup")
    print 'Backing up remote podcast xml files to ', local_path
    remote_path = '/httpdocs/Podcast/'
    download_file(ftp, remote_path, 'chsermon.xml', local_path, today)
    download_file(ftp, remote_path, 'eng_sermon.xml', local_path, today)
    print 'Done.'
 