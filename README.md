# createDirXML.py
1.For a fixed directory with several audio files, use ffmpeg to figure out the duration, mean volume, and maximum volume of each audio file
2.Use that data to create a session.xml to describe the files under the directory
3.Each directory is a session with several audio recordings finished by one person
4.Zip all the files under the directory including the XML file generated and upload that package to AWS S3 for a AWS Lambda function to process

# DirToSessionPackage.py
1.Lists are created to store the name of directories
2.The directory lists are then split into sets of the specified threads
3.Each set if then run simultaneously through multithreading
