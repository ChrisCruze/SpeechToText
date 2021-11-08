import glob
import ntpath
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess
import logging 
import sys 
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO,format=LOG_FORMAT,filemode="w")
logger = logging.getLogger()

#https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
def path_get():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    logger.info('application_path: %s', str(application_path))
    return application_path

def path_combine(arg):
    file_path = os.path.join(path_get(),arg)
    logger.info('file_path: %s', str(file_path))
    return file_path

def glob_get(arg):
    glob_path = os.path.join(path_get(),arg)
    logger.info('glob_path: %s', str(glob_path))
    glob_directories = glob.glob(glob_path)
    logger.info('%s: %s', arg,str(glob_directories))
    return glob_directories


def wav_convert_from_mov(file_name):
    from_file_path = path_combine(file_name+".mov")
    sound = AudioSegment.from_file(from_file_path, "mov")
    export_file_path = path_combine(file_name+".wav")
    sound.export(export_file_path, format="wav")
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
    file_name = path_combine(file_name)
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
    directories = glob_get("*"+extension) #glob.glob("*"+extension)
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

    file_name = path_combine(file_name)
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

def wav_mov_files_unique_get():
    wav_files = extension_remove_directories(glob_get("*.wav"))
    mov_files = extension_remove_directories(glob_get("*.mov"))
    return list(set(mov_files+wav_files))

def mov_wav_files_process():
    mov_wav_file_names = wav_mov_files_unique_get()
    for file_name in mov_wav_file_names:
        convert_file(file_name)

mov_wav_files_process()
#print (wav_mov_files_unique_get())
#convert_file('Tim Goff 110221')








