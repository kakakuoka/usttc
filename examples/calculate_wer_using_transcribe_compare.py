from usttc import AsrClientFactory, AsrProvider, MultiAsrClient
from usttc.audio import AudioFile
from transcription_compare.levenshtein_distance_calculator import UKKLevenshteinDistanceCalculator
from transcription_compare.tokenizer import WordTokenizer
from transcription_compare.local_optimizer.digit_util import DigitUtil
from transcription_compare.local_optimizer.local_cer_optimizer import LocalCerOptimizer


audio = AudioFile(file_path="audio/librivox.wav")
reference_file_path = "audio/ref.txt"


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
multi_asr_client = MultiAsrClient(asr_clients)


def get_token_list(text):
    token_list = WordTokenizer().tokenize(
        token_string=text, brackets_list=["[]", "()", "<>"],  # -b "[]" -b "()" -b "<>"
        to_lower=True, remove_punctuation=True, use_alternative_spelling=True)  # -l -p -u
    return token_list


with open(reference_file_path, "r", encoding='utf-8') as id_file:
    ref_text = id_file.read()
    print("Reference: {}".format(ref_text))
    ref_token_list = get_token_list(ref_text)

results = multi_asr_client.recognize(audio)

for asr_client in asr_clients:
    print("Provider: {}".format(asr_client.provider))
    result = results[asr_client.provider]
    transcript = result.transcript
    print("Transcript: {}".format(transcript))

    output_token_list = get_token_list(transcript)

    error_rate_r = UKKLevenshteinDistanceCalculator(
        tokenizer=WordTokenizer(),
        get_alignment_result=True,
        local_optimizers=[DigitUtil(process_output_digit=True), LocalCerOptimizer()]
    ).get_result_from_list(
        ref_tokens_list=ref_token_list,
        output_tokens_list=output_token_list
    ).error_rate
    print("WER: {}".format(error_rate_r))

