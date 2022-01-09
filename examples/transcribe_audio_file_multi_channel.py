from usttc import AsrClientFactory, AsrProvider, Config
from usttc.audio import AudioFile

asr_client = AsrClientFactory.get_client_from_key_file(
        asr_provider=AsrProvider.GOOGLE,
        filename="<YOUR_GOOGLE_CLOUD_JSON_KEY_FILE_PATH>",
        google_storage_bucket="<YOUR_GOOGLE_STORAGE_BUCKET_NAME>"
    )

audio = AudioFile(file_path="audio/librivox-stereo.wav")
config = Config(
    separate_speaker_per_channel=True
)

try:
    result = asr_client.recognize(audio, config)
    # Get results for each speaker
    for paragraph in result.dialogue:
        print("Speaker-{} : {}".format(paragraph.speaker, paragraph.text))

except Exception as e:
    print(e)
