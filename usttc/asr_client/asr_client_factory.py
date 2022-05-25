from usttc.asr_client.asr_provider import AsrProvider
from usttc.asr_client.google_client import GoogleClient
from usttc.asr_client.voicegain_client import VoicegainClient
from usttc.asr_client.aws_client import AwsClient
from usttc.asr_client.assembly_ai_client import AssemblyAiClient
from usttc.asr_client.azure_client import AzureClient
from usttc.asr_client.rev_client import RevClient
from usttc.asr_client.deepgram_client import DeepgramClient


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
            AsrProvider.MICROSOFT_AZURE: AzureClient
        }
        return provider_map.get(asr_provider)

