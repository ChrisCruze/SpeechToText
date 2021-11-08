import glob
import ntpath
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess
import logging 

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO,format=LOG_FORMAT,filemode="w")
logger = logging.getLogger()



def wav_convert_from_mov(file_name):
    sound = AudioSegment.from_file(file_name+".mov", "mov")
    sound.export(file_name+".wav", format="wav")
    logger.info('Converted %s from MOV to WAV', str(file_name))

def chunks_from_sound(file_name):
    sound = AudioSegment.from_wav(file_name+".wav")  
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    logger.info('Created %s Chunks', str(len(list(chunks))))
    return chunks 

def check_make_folder(folder_name):
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)


def chunks_create_from_file_name(file_name):
    logger.info('Breaking into Chunks')
    chunks = chunks_from_sound(file_name)
    folder_name = file_name#"audio-chunks"
    check_make_folder(folder_name)
    chunk_filenames= []
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        chunk_filenames.append(chunk_filename)
    return chunk_filenames 

def extension_remove_directories(directories):
    return [ntpath.basename(directory).split('.')[0] if '.' in directory else directory.replace('/','') for directory in directories] 

def file_check_extension(file_name,extension):
    directories = glob.glob("*"+extension)
    directories = extension_remove_directories(directories)
    has_file = file_name in directories
    logger.info('%s has %s: %s', str(file_name),str(extension),str(has_file))
    return has_file

def audio_chunk_process(r,chunk_filename):
    with sr.AudioFile(chunk_filename) as source:
        audio_listened = r.record(source)
        try:
            text = r.recognize_google(audio_listened)
        except sr.UnknownValueError as e:
            text = ""
            pass 
            #logger.warn('Error : %s', str(e))
        return text



def get_large_audio_transcription(file_name):
    logger.info('Initiating Recognizer')

    r = sr.Recognizer()

    folder_name = file_name#"audio-chunks"

    logger.info('Creating File and Iterating Through Chunks')

    whole_text = ""
    with open(file_name + '.txt',"a") as f: 
        chunks = os.listdir(file_name)
        for i,file in enumerate(chunks,start=1):
            chunk_filename = os.path.join(folder_name, f"{i}.wav")
            # logger.info('%s',chunk_filename)
            text = audio_chunk_process(r,chunk_filename)
            f.write(text +' ')
            logger.info('%s : %s', str(i) + "/" + str(len(chunks)),str(text))
            whole_text += text
    return whole_text


def convert_file(file_name):
    has_wav_file = file_check_extension(file_name,'.wav')
    if not has_wav_file:
        wav_convert_from_mov(file_name)

    has_chunks = file_check_extension(file_name,'/')
    if not has_chunks: 
        chunks_create_from_file_name(file_name)

    has_text = file_check_extension(file_name,'.txt')
    if not has_text:
        get_large_audio_transcription(file_name)

convert_file('Tim Goff 110221')










# file_check_extension(file_name,'/')

# file_check_extension('jarvis_intro','.txt')

def files_to_convert_get(base,target):
    mov_files = glob.glob("*"+base)
    wav_files = glob.glob("*"+target)

    mov_files = extension_remove_directories(mov_files)
    wav_files = extension_remove_directories(wav_files)
    logger.info('Identifying %s files: %s', str(base),str(mov_files))
    logger.info('Identifying %s files: %s', str(target),str(wav_files))
    mov_files = [mov_file for mov_file in mov_files if mov_file not in wav_files]
    logger.info('Remaining files: %s', str(mov_files))
    return mov_files

def mov_files_to_convert_get():
    return files_to_convert_get('.mov','.wav')

def wav_files_to_convert_get():
    return files_to_convert_get('.wav','.txt')

def wav_files_to_convert_get_chunk():
    return files_to_convert_get('.wav','/')


def write_file(file_name,text):
    path = file_name + '.txt'
    file_object = open(path,"w+")
    file_object.write(text)
    file_object.close()







def txt_convert_from_wav(file_name):
    txt = get_large_audio_transcription(file_name)
    print (txt)
    #write_file(file_name,txt)
    



def run():
    mov_files = mov_files_to_convert_get()
    [wav_convert_from_mov(mov_file) for mov_file in mov_files]
    wav_files = wav_files_to_convert_get()
    chunk_files = wav_files_to_convert_get_chunk()
    [chunks_create_from_file_name(chunk_file) for chunk_file in chunk_files]
    [txt_convert_from_wav(wav_file) for wav_file in wav_files]




# print (os.listdir('Tim Goff 1102211'))
# print (glob.glob('Tim Goff 1102211'))
#wav_files_to_convert_get_chunk()
#print (glob.glob("*/"))
#run()