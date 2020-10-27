# Sophia Cheng, sophiacheng@analyticmeasures.com Sept 13, 2020

import os
from multiprocessing import Process
import createDirXML

dirName = '/home/ubuntu/work'
dirStudents = dirName + '/students'
dirAudioMetaData = dirName + '/audio_metadata.csv'
dirAudioLocation = dirName + '/audio-files'
nThreads = 36

fileName = []
passageID = []
length = []
grade = []
year = []

with open(dirAudioMetaData, newline = '') as f:
    next(f)
    for line in f.readlines():
        currentLine = line.split(',')
        currentLine[0] = currentLine[0].split('/')[-1]
        if(len(currentLine[0].split('_')) != 5):
            print("Warning: wrong format - ", currentLine[0])
        currentLine[0] = currentLine[0].replace(".wav", ".opus")
        fileName.append(currentLine[0])
        passageID.append(currentLine[1])
        length.append(currentLine[2])
        grade.append(currentLine[3])
        year.append(currentLine[4].split('\n')[0].split()[0])

for i, file in enumerate(fileName):
    studentID = file.split('_')[1]
   # if(studentID == '299' or studentID == '527' or studentID =='531'):
    audio_location = dirAudioLocation + '/' + file
    if not os.path.isfile(audio_location):
        print("WARNING: no audio file at ", audio_location)
    else:
        student_location = dirStudents + '/' + studentID + '_' + year[i]
        if (os.path.isdir(student_location) == False):
            os.makedirs(student_location)
        item = file.split('_')[3]
        newfileName = '3026.' + item + '.' + file.split('_')[4]
        os.system("mv " + audio_location + " " + student_location + '/' + newfileName)


dirList = []
for directories in os.listdir(dirStudents):
    dirList.append(dirStudents + '/' + directories)

def handleOneDir(oneSet):
  for oneDir in oneSet:
    createDirXML.createDirXML(oneDir)

n = int(len(dirList)/nThreads)
sets = [dirList[i:i+n] for i in range(0, n*nThreads, n)]  # split to nThreads
t = dirList[n*nThreads:]
if len(t) > 0:
  for i, e in enumerate(t):
    sets[i].append(e)

processes = []
for oneSet in sets:
  p = Process(target=handleOneDir, args=(oneSet,))
  p.start()
  processes.append(p)

for p in processes:
  p.join()