from asr_bridge.asr_client.asr_provider import AsrProvider
from asr_bridge.asr_client.google_client import GoogleClient
from asr_bridge.asr_client.voicegain_client import VoicegainClient
from asr_bridge.asr_client.aws_client import AwsClient


class AsrClientFactory:

    @staticmethod
    def get_client_from_key_file(asr_provider: AsrProvider, filename: str, *args, **kwargs):
        return AsrClientFactory.get_provider_client(asr_provider).from_key_file(filename, *args, **kwargs)

    @staticmethod
    def get_client_from_key(asr_provider: AsrProvider, key: str, *args, **kwargs):
        return AsrClientFactory.get_provider_client(asr_provider).from_key(key, *args, **kwargs)

    @staticmethod
    def get_provider_client(asr_provider: AsrProvider):
        if asr_provider == AsrProvider.GOOGLE:
            return GoogleClient
        if asr_provider == AsrProvider.VOICEGAIN:
            return VoicegainClient
        if asr_provider == AsrProvider.AMAZON_AWS:
            return AwsClient
