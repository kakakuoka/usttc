

class AsrBridgeException(Exception):
    pass


class AudioException(AsrBridgeException):
    pass


class ASRException(AsrBridgeException):
    pass


class ConfigurationException(AsrBridgeException):
    pass
