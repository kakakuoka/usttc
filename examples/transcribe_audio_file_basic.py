"""
Use 6 providers to transcribe an audio file.
If your audio is stereo (2-channels), two channels are merged before transcribe.
"""
from usttc import AsrClientFactory, AsrProvider
from usttc.audio import AudioFile

asr_clients = [
    AsrClientFactory.get_client_from_key_file(
        asr_provider=AsrProvider.GOOGLE,
        filename="<YOUR_GOOGLE_CLOUD_JSON_KEY_FILE_PATH>",
        google_storage_bucket="<YOUR_GOOGLE_STORAGE_BUCKET_NAME>"
    ),
    AsrClientFactory.get_client_from_key(
        asr_provider=AsrProvider.VOICEGAIN,
        key="<YOUR_VOICEGAIN_JWT_TOKEN>"
    ),
    AsrClientFactory.get_client_from_key(
        asr_provider=AsrProvider.AMAZON_AWS,
        key="<YOUR_AWS_USER_ACCESS_KEY_ID>",
        aws_secret_access_key="<YOUR_AWS_USER_SECRET_ACCESS_KEY>",
        region_name='<YOUR_S3_BUCKET_REGION>',
        s3_bucket='<YOUR_S3_BUCKET_NAME>'
    ),
    AsrClientFactory.get_client_from_key(
        asr_provider=AsrProvider.REV,
        key="<YOUR_REV_ACCESS_TOKEN>"
    ),
    AsrClientFactory.get_client_from_key(
        asr_provider=AsrProvider.ASSEMBLY_AI,
        key="<YOUR_ASSEMBLY_AI_API_KEY>"
    ),
    AsrClientFactory.get_client_from_key(
        asr_provider=AsrProvider.DEEPGRAM,
        key="<YOUR_DEEPGRAM_API_KEY>"
    ),
]

audio = AudioFile(file_path="audio/librivox.wav")  # you can use (almost) any audio format
for asr_client in asr_clients:
    print("Provider: {}".format(asr_client.provider))
    try:
        result = asr_client.recognize(audio)
        # Get transcribe results
        print("Result: {}".format(result.transcript))

        # # You can also get words with timestamp
        # for word in result.words:
        #     print("Word detail result:", word.text, word.start, word.end, word.confidence)

    except Exception as e:
        print(e)
