from uni_transcribe.asr_client.asr_provider import AsrProvider
from uni_transcribe.asr_client.google_client import GoogleClient
from uni_transcribe.asr_client.voicegain_client import VoicegainClient
from uni_transcribe.asr_client.aws_client import AwsClient
from uni_transcribe.asr_client.assembly_ai_client import AssemblyAiClient
from uni_transcribe.asr_client.azure_client import AzureClient
from uni_transcribe.asr_client.rev_client import RevClient
from uni_transcribe.asr_client.deepgram_client import DeepgramClient
from uni_transcribe.asr_client.watson_client import WatsonClient


class AsrClientFactory:

    @staticmethod
    def get_client_from_key_file(asr_provider: AsrProvider, filename: str, *args, **kwargs):
        return AsrClientFactory.get_provider_client(asr_provider).from_key_file(filename, *args, **kwargs)

    @staticmethod
    def get_client_from_key(asr_provider: AsrProvider, key: str, *args, **kwargs):
        return AsrClientFactory.get_provider_client(asr_provider).from_key(key, *args, **kwargs)

    @staticmethod
    def get_provider_client(asr_provider: AsrProvider):
        provider_map = {
            AsrProvider.GOOGLE: GoogleClient,
            AsrProvider.VOICEGAIN: VoicegainClient,
            AsrProvider.AMAZON_AWS: AwsClient,
            AsrProvider.REV: RevClient,
            AsrProvider.DEEPGRAM: DeepgramClient,
            AsrProvider.ASSEMBLY_AI: AssemblyAiClient,
            AsrProvider.MICROSOFT_AZURE: AzureClient,
            AsrProvider.IBM_WATSON: WatsonClient,
        }
        return provider_map.get(asr_provider)

