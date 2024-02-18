import subprocess

def convert_webm_to_mp4(webm_file_path, output_mp4_path):
    command = ['ffmpeg', '-i', webm_file_path, '-c:v', 'copy', '-c:a', 'aac', output_mp4_path]
    subprocess.run(command, check=True)

def extract_audio_from_webm(webm_file_path, output_wav_path):
    command = ['ffmpeg', '-i', webm_file_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_wav_path]
    subprocess.run(command, check=True)

# Replace 'input.webm' with your .webm file path
webm_file = 'input.webm'
mp4_file = 'output.mp4'
wav_file = 'output.wav'

convert_webm_to_mp4(webm_file, mp4_file)
extract_audio_from_webm(webm_file, wav_file)

print("Conversion complete")
