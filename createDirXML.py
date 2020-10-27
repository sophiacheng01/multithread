#! /usr/bin/env python3
# Sophia Cheng, June 29, 2020
# sophiacheng@analyticmeasures.com
import datetime
import time
import random
import os
import subprocess

def audio_duration(fn):
  cmd = "ffmpeg -i " + fn + " 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//"
  proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
  (out, err) = proc.communicate()
  dds = out.decode().split('\n')[0].split(":")
  # print(dds)
  dlength = float(dds[2]) + float(dds[1]) * 60 + float(dds[0]) * 60 * 60
  return dlength

def audioVolumes(audioFN):
  cmd = "ffmpeg -i " + audioFN + " -af 'volumedetect' -vn -sn -dn -f null /dev/null 2>&1 | grep volumedetect"
  proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
  (out, err) = proc.communicate()
  lines = out.decode().splitlines()
  avolume = -99
  mvolume = -99
  for idxa, line in enumerate(lines):
    elements = line.split(" ")
    if "mean_volume:" in line:
      avolume = elements[4]
    if "max_volume:" in line: 
      mvolume = elements[4]
  return avolume, mvolume

def createDirXML(dirName): 
  
  sid = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S') + "-" + ''.join(random.sample('0123456789', 5))

  startTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"')[:-4]
  sst = startTime

  sst_time = datetime.datetime.strptime(sst, "%Y-%m-%d %H:%M:%S.%f").timestamp()

  est = ''
  xmlString = ''
  sst = startTime.replace('T', ' ').replace('Z', '') + " +0000"
  for ofn in os.listdir(dirName):
    if(ofn == 'session.xml'): continue
    dlength = audio_duration(dirName + '/' + ofn)
    item = ofn.split('.')[1]
    print("item ", item, dlength)

    nfn = ofn
    sst = datetime.datetime.fromtimestamp(sst_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " +0000"
    est = datetime.datetime.fromtimestamp(sst_time + dlength).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " +0000"
    sst_time = sst_time + dlength

    avol, mvol = audioVolumes(dirName + '/' + ofn)

    if(xmlString == ''): sst=startTime + " +0000"
    originalItem = item
    if(len(item) == 6):
      item = item[1:]

    newfileName = '3026.' + item + '.opus'

    xmlString += "    <response type='3026' item='" + item + "' oItem='" + originalItem + "' itemType='AudioResponse' extra='"+ ofn.split('.')[2] +  "' status='UNKNOWN' startTime='" + sst +"' endTime='" + est + "' avgVolume='" + str(avol) + "' maxVolume='" + str(mvol) + "'>\n      <afilename>" + newfileName + "</afilename>\n    </response>\n"

    os.system("mv " + dirName + '/' + ofn + " " + dirName + '/' + newfileName)
    os.system("ffmpeg -y -loglevel panic -i " + dirName+"/"+newfileName + " -af loudnorm "+ sid+ "Temp.opus; mv "+sid+"Temp.opus " + dirName + "/" + newfileName)

  xmlString += "  </responses>\n</session>\n"
  fxml = open(dirName + "/session.xml", 'w')
  fxml.write("<?xml version='1.0'?>\n")
  fxml.write("<session id='" + sid + "' name='xx' startTime='" + startTime + " +0000' endTime='" + est + "' status='COMPLETED'>\n")
  # some dummy information
  fxml.write("  <device>\n    <pin>" + dirName.split('/')[-1].split('_')[0]  + "</pin>\n" )
  fxml.write("    <year>" + dirName.split('/')[-1].split('_')[1] + "</year>\n" )
  fxml.write("    <uid>xx</uid>\n    <model>xx HTML5</model>\n    <name>Reading</name>\n    <systemName>UNKNOWN</systemName>\n    <systemVersion>1</systemVersion>\n    <app>\n      <buildTime>Sep 02 2020</buildTime>\n    </app>\n  </device>\n  <email>xxx@xxx.com</email>\n  <responses>\n")
  fxml.write(xmlString)
  fxml.close()
  #f.close()

  os.system("mv " + dirName + " " + sid)

  for file in os.listdir(sid):
    if(len(file.split('.')) == 4):
      os.system("rm " + sid + '/' + file)

  os.system("zip -r -j " + sid + ".zip " + sid)

  cmd = "aws s3 cp " + sid + ".zip s3://xxx-incoming"; print(cmd); os.system(cmd)
