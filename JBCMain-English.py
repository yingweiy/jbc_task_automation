# -*- coding: utf-8 -*-
"""
Created on Sun Mar 09 21:40:30 2014

@author: yyu
"""

import sys
sys.path.append('C:\jbc_task_automation\Python')
import JBCWebAutomation as jbc

today=jbc.GetToday()
# to override the date: today='140305'

###################################################################
print 'Start job for date ' + today +'...'
jbc.ConvertSermonDOC2PDF(today, 0) # 0 for English
ftp = jbc.JBCFTPConnection()
jbc.uploadJBCWeb(ftp, today, 0, 'pdf')
mp3today='20'+today[0:2]+'_'+today[2:6]
jbc.uploadJBCWeb(ftp, mp3today, 0, 'mp3')
jbc.backup_podcast_xml(ftp, today)
print 'Finshed job.'
ftp.close()
raw_input("Press Enter to continue...")