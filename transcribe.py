from moviepy.editor import VideoFileClip
import whisper
import requests
import os

def extract_audio(video_file, output_audio_file):
    # Load the video file
    video = VideoFileClip(video_file)
    
    # Extract the audio
    audio = video.audio
    
    # Write the audio file
    audio.write_audiofile(output_audio_file)
    
    # Close the clips
    video.close()
    audio.close()

def download_video(url, output_file):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Open a file in write-binary mode
        with open(output_file, 'wb') as file:
            # Write the content to the file in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"Download complete: {output_file}")
    else:
        print(f"Failed to download video. Status code: {response.status_code}")

def transcribe_video(mp4_title, mp4_url):
    # Use pyav to extract audio
    audio_file = "extracted_audio.wav"
    video_file = "downloaded_video.mp4"
    download_video(mp4_url, video_file)
    extract_audio(video_file, audio_file)
    # Load Whisper model
    model = whisper.load_model("base")
    # Transcribe audio
    result = model.transcribe(audio_file)
    transcription = result["text"]

    with open(f"{mp4_title} - Transcript.txt", "w+") as f:
      f.write('-' * 100 + '\n')
      f.write(mp4_title + '\n')
      f.write(f"Video URL: {mp4_url}" + '\n')
      f.write('-' * 100 + '\n')
      for sentence in transcription.split('.'):
        if sentence:
          f.write(sentence + '.\n')
    # Clean up
    os.remove(audio_file)
    os.remove(video_file)
    # Return the transcription
    return result['text']

# Usage
mp4_title = "Environment and LLMs Part 1: Course Environment"
mp4_url = "https://d36m44n9vdbmda.cloudfront.net/assets/s-fx-15-v1/RAG-Videos/RAG_01_Environment.mp4"
transcription = transcribe_video(mp4_title, mp4_url)
print(transcription)
