import speech_recognition as sr 
import os, time
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
# import cv2
# import pandas as pd
import moviepy.editor as mp
from googletrans import Translator

import srt # https://srt.readthedocs.io/en/latest/api.html
from datetime import timedelta

from xtimer import Timer
import json, shutil, glob, math



############################# language configuration #############################################
## You can find all the possible languages here:
# https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
# e.g., en, zh-cn, ja
detect_language = "ja"

## You can find all the possible language here:
# https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages
# e.g., en, zh-cn, ja
source_language = "ja"
target_language = "en"
############################# language configuration #############################################

# set True for speech intense videos (e.g., presentation)
# then you will get a txt file that is translated each 2min
translate_as_whole = False 



translator = Translator()
r = sr.Recognizer()
# https://realpython.com/python-speech-recognition/#how-speech-recognition-works-an-overview
# https://stackoverflow.com/questions/14257598/what-are-language-codes-in-chromes-implementation-of-the-html5-speech-recogniti





def get_thd_min_silence(p, default=True):
  # 25, 1200 first attempt
  thd = 25 # larger more sensitive
  min_silence_len=1000
  sub_name = p[:-3]+f"{thd}_{min_silence_len//100}_x2.srt"
  if default:
    sub_name = p[:-3]+"srt"
  
  return thd, min_silence_len, sub_name



def shorten_voice(nonsilent_data, max_interval=10000):

  new_data = []

  buffer_time = 2000
  for start_time, end_time in nonsilent_data:

    while end_time - start_time >= max_interval:
      new_end = start_time + max_interval + buffer_time
      new_start = start_time

      new_data.append((new_start, new_end, True))
      start_time += max_interval
    # else:
    new_data.append((start_time, end_time, False))
  
  return new_data

#  print(len()




def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)



def get_large_audio_transcription(aud_path, ext="wav", is_dense=False):
  """
  Splitting the large audio file into chunks
  and apply speech recognition on each of these chunks
  """
  # open the audio file using pydub
  sound = AudioSegment.from_wav(aud_path)
  # print(sound.channels)
  # sound = sound.set_channels(1)
  # print(sound.channels)
  # return
  # .resample(sample_rate_Hz="28000", sample_width=None, channels=1) #wav
  # split audio sound where silence is 700 miliseconds or more and get chunks
  # https://stackoverflow.com/questions/59102171/getting-timestamps-from-audio-using-python
  #normalize audio_segment to -20dBFS 
  normalized_sound = match_target_amplitude(sound, -20.0) #-20.0
  print("length of audio_segment={} seconds".format(len(normalized_sound)/1000))

  folder_path = '/'.join(aud_path.split('/')[:-1])
  audio_name = aud_path.split('/')[-1][:-4]

  tmp_path = folder_path+f'/##{audio_name}_tmp'

  if not os.path.isdir(tmp_path):
    os.mkdir(tmp_path)

  nonslient_file = f'{tmp_path}/detected_voice.json'

  thd, min_slien, sub_name = get_thd_min_silence(aud_path)

  if os.path.exists(nonslient_file):
    with open(nonslient_file, 'r') as infile:
      nonsilent_data = json.load(infile)
  
  else:
    
    nonsilent_data = detect_nonsilent(normalized_sound, min_silence_len=min_slien, silence_thresh=-20.0 - thd, seek_step=1)

    nonsilent_data = shorten_voice(nonsilent_data)

    with open(nonslient_file, 'w') as outfile:
      json.dump(nonsilent_data, outfile)

  print(f"n_detected_voice: {len(nonsilent_data)}")
  tim.lap()
  
  # create a directory to store the audio chunks
  
  whole_text = ""
  whole_trans = ""
  # f_lines = open(f"{tmp_path}/lines.txt", 'w', encoding="utf-8")
  # f_subs = open(f"{folder_name}/{folder_name}.srt", 'w', encoding="utf-8")
  

  subs = []
  # process each chunk 
  for i, duration in enumerate(nonsilent_data, start=1):
    # continue
    # export audio chunk and save it in
    # the `folder_name` directory.

    start_time, end_time, buffered = duration
    start_min = start_time//1000/60
    end_min = end_time//1000/60
    i_covered = i/len(nonsilent_data)*100
    time_covered = start_time/len(normalized_sound)*100
    print('='*12+f" Index[{i}]~{i_covered:0.1f}%: {start_min:.2f}-{end_min:.2f}m~{time_covered:.1f}%"+'='*12)

    chunk_filename = tmp_path + f"/c{i}_{start_time//1000}_{end_time//1000}."+ext # os.path.join(tmp_path, f"c{i}_{start_time}_{end_time}."+ext)

    
    add_vol = 10
    audio_chunk = normalized_sound[start_time:end_time] + add_vol
    audio_chunk.export(chunk_filename, format=ext)
    
    # recognize the chunk
    with sr.AudioFile(chunk_filename) as source:
      audio_listened = r.record(source)
      # try converting it to text
      try:


#################### modify language= to define the language to detect ##########
## You can find all the possible languages here:
# https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
        text = r.recognize_google(audio_listened, language=detect_language)
#################### modify language= to define the language to detect ##########


        # recognize_bing, recognize_google(), recognize_google_cloud(), recognize_ibm(), recognize_sphinx()
      except sr.UnknownValueError as e:
        print("Recognize Error: ", str(e), end = '; ')
        continue
      except Exception as e:
        print("Recognize Error:", str(e), end = '; ')
        continue

      # else:
      text = f"{text.capitalize()}. "#.decode('utf-8').encode('gbk')
      try:
        print(text)

#################### modify src='ja', dest="zh-cn" to define the source and target language ##########
## You can find all the possible language here:
# https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages
        transd = translator.translate(text, src=source_language, dest=target_language) # en zh-cn
#################### modify src='ja', dest="zh-cn" to define the source and target language ##########


      except Exception as e:
        print("Translate Error:", str(e))
        continue

      result = transd.text #.decode('utf-8').encode('gbk')


      
      print(result)

      # subtitles
      combo_txt = text + '\n' + result + '\n\n'

      if buffered:
        # start_time += 2000
        end_time -= 2000
      start = timedelta(milliseconds=start_time)
      end = timedelta(milliseconds=end_time)

      # print(combo_txt)

      index = len(subs)+1
      # print(index)
      sub = srt.Subtitle(index=index, start=start, end=end, content=combo_txt)
      subs.append(sub)

      tim.lap()

      whole_text += text
      whole_trans += result





  final_srt = srt.compose(subs)
  with open(sub_name, 'w', encoding="utf-8") as f:
    f.write(final_srt)
  



  if is_dense:
    sub_name = aud_path[:-3]+f"_whole.txt"
    chunk_filename = tmp_path + f"/c{i}_{0//1000}_{len(normalized_sound)//1000}."+ext
    detect_trans_as_whole(normalized_sound, chunk_filename, sub_name=sub_name, ext=ext)

  

  
  # final_srt = srt.compose(subs)
  # print(final_srt)

  shutil.rmtree(tmp_path)
  os.remove(aud_path)


  return whole_text, whole_trans





def detect_trans_as_whole(normalized_sound, chunk_filename, sub_name, ext):
  print("$"*30)
  print("Detect and translate as a whole:")
  print("$"*30)

  sem_len = 1000 * 120
  tot_len = len(normalized_sound)

  add_vol = 10

  org_txt = ""
  trans_txt = ""

  seg_no = 0

  for start_t in range(0, tot_len, sem_len):
    end_t = start_t + sem_len
    audio_chunk = normalized_sound[start_t:end_t] + add_vol
    audio_chunk.export(chunk_filename, format=ext)
    
    # recognize the chunk
    with sr.AudioFile(chunk_filename) as source:
      audio_listened = r.record(source)
      # try converting it to text

    try:
      text = r.recognize_google(audio_listened, language=detect_language)
    except sr.UnknownValueError as e:
      print("Recognize Error: ", str(e), end = '; ')
      
    except Exception as e:
      print("Recognize Error:", str(e), end = '; ')

    try:
      print(text)
      org_txt += f" ### {seg_no} ### "
      org_txt += text

      transd = translator.translate(text, src=source_language, dest=target_language) # en zh-cn

    except Exception as e:
      print("Translate Error:", str(e))

    print(transd.text)
    trans_txt += f" ### {seg_no} ### "
    trans_txt += transd.text

    seg_no += 1
    


  with open(sub_name, 'w', encoding="utf-8") as f:
    f.write(org_txt + "\n" + trans_txt)
    # f.write()
    # f.write()
  
  return text, transd



    



def get_subtitle_from_dense_speech(aud_path, ext="wav"):
  """
  1. detect speech segments
  2. combine them to regconise, and translate
  3. segment them to subtitles
  """
  # todo

  return






def get_sub_given_path(p):

  # path = "mrhp011_4_1.mp4"
  a_name = p[:-4]+".wav"

  if not os.path.exists(a_name):
    clip = mp.VideoFileClip(p)
    aud = clip.audio.write_audiofile(a_name, buffersize=20000)
  
  print(a_name, "generated.")
  tim.lap()
  # print(path[-3:])
  # print(dir(AudioSegment))
  # 'from_flv', 'from_mono_audiosegments', 'from_mp3', 'from_ogg', 'from_raw', 'from_wav'
  print("\nFull text:", get_large_audio_transcription(a_name, ext="wav", is_dense=translate_as_whole))





def get_ps(folder):
  extens = ["mp4", "avi", "wmv", "mkv", "rmvb", "mpg"]
  ps = []

  for exten in extens:
    ps += glob.glob(f"{folder}**/*.{exten}", recursive=True)
  
  ps = [pps.replace("\\", "/") for pps in ps]


  return ps, ps



def search_nc(folders_nc, spn="others"):
  # with open(f"{spn}.txt", 'a') as f:
  #   f.write('\n'+str(date.today())+'\n')
  check_exist = True


  print(folders_nc)
  num_subs = 0
  for f in folders_nc:
    print('='*30, "Searching", f, '='*20)
    ps_clean, ps = get_ps(f)

    # print(ps)

    for pc, p in zip(ps_clean, ps):
      # print(p)
      last_c = p.split('.')[-2][-2:].lower()
      nc = True # last_c[-1] != 'c' and last_c[-2:] != 'ch'
      psz = os.path.getsize(p)/(2**30)
      nhd = psz < 3.0
      if nc: #or (not nc and nhd):
        print(p)
        print(round(psz, 2), "GB")
        _, _, sub_name = get_thd_min_silence(p)

        covered_i = 20
        if num_subs == covered_i:
          check_exist = False

        
        if check_exist and os.path.exists(sub_name):
          print(f"The subs already generated!")
          num_subs += 1
          print(num_subs)
          continue
        else:
          get_sub_given_path(p)
          num_subs += 1
          print(f"{num_subs} subs generated.")

        
        # 2351s per movie
        # 2920s
        print("="*10+f"{tim.total_t()/num_subs:.1f} s per movie" + "="*10)
        


# https://stackoverflow.com/questions/67009452/adding-subtitles-to-video-with-python
# https://towardsdatascience.com/extracting-audio-from-video-using-python-58856a940fd

# ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4
if __name__ == "__main__":
  tim = Timer()
  tim.start()


####### modify here for your searching folder #######
  folders = ["source/"]
####### modify here for your searching folder #######

  search_nc(folders)

  tim.stop()

