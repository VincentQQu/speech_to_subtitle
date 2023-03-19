# Speech to Subtitle
This is a repository for an automatic program to extract speech from video, translate, and generate subtitle file.


### Work Flow
1. Extract audio from video.
2. Extract sound segments in the audio.
3. Recognize speech segment by segment (use SpeechRecognition to recognize Japanese by default but you can modify language in line 150).
4. Translate to target language (from Japanese to English by default but you can modify language in line 170).
5. Save as srt format.

### Requirements
googletrans==4.0.0rc1, moviepy==1.0.3, pydub==0.25.1, SpeechRecognition==3.10.0, srt==3.5.2


### How to Use
0. Run **pip3 install -r requirements.txt** in terminal to install required packages
1. Put your videos into folder **source**.
2. Run **python3 speech_to_txt.py** in terminal to process all videos in source folder.
3. Srt file will then be in source folder.

**Note:** You can modify line 315 to add more source folders.


### To Be Updated
