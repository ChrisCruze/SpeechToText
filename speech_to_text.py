import glob
import ntpath
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess

def extension_remove_directories(directories):
    return [ntpath.basename(directory).split('.')[0] for directory in directories] 

def files_to_convert_get(base,target):
    mov_files = glob.glob("*."+base)
    wav_files = glob.glob("*."+target)
    mov_files = extension_remove_directories(mov_files)
    wav_files = extension_remove_directories(wav_files)
    mov_files = [mov_file for mov_file in mov_files if mov_file not in wav_files]
    return mov_files

def mov_files_to_convert_get():
    return files_to_convert_get('mov','wav')

def wav_files_to_convert_get():
    return files_to_convert_get('wav','txt')

def write_file(file_name,text):
    path = file_name + '.txt'
    file_object = open(path,"w+")
    file_object.write(text)
    file_object.close()
    

def wav_convert_from_mov(file_name):
    sound = AudioSegment.from_file(file_name+".mov", "mov")
    sound.export(file_name+".wav", format="wav")

def get_large_audio_transcription(file_name):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    path = file_name+".wav"
    r = sr.Recognizer()
    sound = AudioSegment.from_wav(path)  
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    folder_name = file_name#"audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                whole_text += '\n'
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    return whole_text

def txt_convert_from_wav(file_name):
    txt = get_large_audio_transcription(file_name)
    write_file(file_name,txt)
    
def run():
    mov_files = mov_files_to_convert_get()
    print (mov_files)
    [wav_convert_from_mov(mov_file) for mov_file in mov_files]
    wav_files = wav_files_to_convert_get()
    print (wav_files)
    [txt_convert_from_wav(wav_file) for wav_file in wav_files]
    
run()