import os
import time
import struct
import sys
import yaml
import io
import pvporcupine
from google.cloud import speech_v1 as speech
from voiceflow import Voiceflow
from pixels import Pixels
import audio
RATE = 16000
language_code = "en-US"  # a BCP-47 language tag
os.chdir("/home/pi/rpi-voice-assistant" )

def load_config(config_file=os.path.join(os.getcwd(),"config.yaml")):
    with open(config_file) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        return yaml.load(file, Loader=yaml.FullLoader)


def main():
    config = load_config()
    # Default Wakeword setup
    porcupine = pvporcupine.create(access_key=config["accesskey"],keywords=config["wakewords"])
    # Custom Wakeword setup
    # porcupine = pvporcupine.create(access_key=config["accesskey"],keyword_paths=[os.path.join(os.getcwd(),"wakeword/Hey-Voice-flow_en_raspberry-pi_v2_1_0.ppn")])
    CHUNK = porcupine.frame_length  # 512 entries
    RATE = porcupine.sample_rate
    # Voiceflow setup
    vf = Voiceflow(config["vf_APIKey"], config["vf_VersionID"])
    start = 0
    # Google ASR setup
    google_asr_client = speech.SpeechClient.from_service_account_file("gc.json")
    google_asr_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=google_asr_config, interim_results=True
    )
    with audio.MicrophoneStream(RATE, CHUNK) as stream:
        pixels.wakeup()
        time.sleep(5)
        pixels.off()
        print("Starting voice assistant!")
        audio.beep()
        audio.beep()
        audio.beep()
        while True:
            try:
                pcm = stream.get_sync_frame()
                if len(pcm) == 0:
                    # Protects against empty frames
                    continue
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Wakeword Detected")
                    pixels.wakeup()
                    pixels.think()
                    audio.beep()
                    end = False
                    while not end:
                        if start==0:
                            # First session
                            print("Initializing first session")
                            response = vf.init_state()
                            start = 1
                        else:
                            stream.start_buf()  # Only start the stream buffer when we detect the wakeword
                            audio_generator = stream.generator()
                            requests = (
                                speech.StreamingRecognizeRequest(audio_content=content)
                                for content in audio_generator
                            )

                            responses = google_asr_client.streaming_recognize(streaming_config, requests)

                            # Now, put the transcription responses to use.
                            utterance = audio.process(responses)
                            stream.stop_buf()

                            # Send request to VF service and get response
                            response = vf.interact(utterance)
                        for item in response:
                            if item["type"] == "speak":
                                payload = item["payload"]
                                if item["payload"]["type"] == "audio":
                                    audio.playUrl(payload["src"])
                                    pixels.speak()
                                else:
                                    message = payload["message"]
                                    print("Response: " + message)
                                    pixels.speak()
                                    audio.play(payload["src"])
                            elif item["type"] == "end":
                                print("-----END-----")
                                end = True
                                pixels.off()
                                start = 0
                                audio.beep()
            except KeyboardInterrupt:
                break

        Pixels.off
        print("")
        print("------------------")
        print("Assistant shutdown")
        print("------------------")

if __name__ == "__main__":
    pixels = Pixels()
    pixels.off()
    main()
