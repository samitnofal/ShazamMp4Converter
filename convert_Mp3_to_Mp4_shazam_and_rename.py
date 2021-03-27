
__author__ = "Sami Nofal"
__copyright__ = "Copyright (C) 2021 Sami Nofal"
__version__ = "1.0"

import os
from moviepy.editor import *
from ShazamAPI import Shazam
import json
import re
import subprocess

def ExtractMusic(vidPath):
    video = VideoFileClip(os.path.join(vidPath))
    vidName = vidPath.split(".mp4")[0]
    vidNameMp3 = vidName +'.mp3'
    video.audio.write_audiofile(vidNameMp3)
    return vidNameMp3

def ShazamMusic(mp3Path, unknown_tracks):
    mp3_file_content_to_recognize = open(mp3Path, 'rb').read()
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    idx=0
    while idx<5:
       j=(next(recognize_generator)) # current offset & shazam response to recognize requests
       idx+=1
    if(j[1] and 'track' in j[1] and len(j[1]['track']['title'])>0):
        print(j[1]['track']['title'])
        mp3Path_old = mp3Path
        mp3Path = re.split("[\w-]+\.mp3", mp3Path_old)[0]
        songTitle=j[1]['track']['title'].replace("/","")
        songTitle = songTitle.replace(" ","_")
        new_path = mp3Path +"/"+songTitle + '.mp3'
        os.rename(mp3Path_old, new_path)
    else:
        unknown_tracks+=1
        new_path = 'unkown_track_'+str(unknown_tracks)+'.mp3'
        os.rename(mp3Path, new_path)
    
    return [new_path, unknown_tracks]

# This function will populate the clean list of videos we will be converting from mp4 to mp3.
def generateMp4CleanList(path_to_check=None):
    filtered_list_files=[]
    if path_to_check == None:
        path_to_check = os.getcwd()

    list_files = os.listdir(path_to_check)

    for each_file in list_files:
        splitted_file_extension = each_file.split(".")
        if (splitted_file_extension[-1] in ["mp4"]):
           filtered_list_files.append(os.path.join(path_to_check, each_file))
    return filtered_list_files

# This function will convert the list of mp4 videos populated above to mp3 songs.
# WARNING: this function expect mp4_file_list to be sanitized and only have mp4 files.
def convertMp4MusicListToMp3List(mp4_file_list):
    mp4F = mp4_file_list
    mp3_file_list = []
    for mp4FileName in mp4F:
        mp4FileName = mp4FileName.strip("\n")
        if os.path.exists(mp4FileName):
            mp3FileName = ExtractMusic(mp4FileName)
            mp3_file_list.append(mp3FileName + "\n")
    return mp3_file_list

# This function will shazam the mp3 songs and will rename it.
def shazamAndRename(mp3_file_list):
    mp3F = mp3_file_list
    song_number=1
    unknown_tracks=0
    for mp3Fame in mp3F:
        mp3Fame = mp3Fame.strip("\n")
        splitted_file_extension = mp3Fame.split(".")
        if (splitted_file_extension[-1] in ["mp3"]):
            if os.path.exists(mp3Fame):
                print(mp3Fame)
                number_of_unknown = unknown_tracks
                mp3FileName, unknown_tracks = ShazamMusic(mp3Fame, unknown_tracks)
                print("Processing song number: " + str(song_number))
                if number_of_unknown == unknown_tracks:
                    print("Success File:" + mp3FileName) 
                else:
                    print("Unkown Track # : " + str(unknown_tracks))
                song_number+=1

def main(argv):

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--pathToFile', 
        default=os.getcwd(),
        help='Path to Mp4 File'
    )
    args = parser.parse_args()

    print("Processing the following file: {FileToProcess}".format(
        FileToProcess=args.pathToFile)
    )

    mp4List = generateMp4CleanList(args.pathToFile)
    print("Generated Mp4 List Successfully")

    mp3List = convertMp4MusicListToMp3List(mp4List)
    print("Coverted Mp4 List to Mp3 Successfully")

    shazamAndRename(mp3List)
    print("Coverted Mp4 to Mp3 Successfully")

if __name__=="__main__":
    main(sys.argv[1:])