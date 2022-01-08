# USTTC (Unified Speech-to-Text Client)

This project provides a simple and unified client wrapper for different Speech-to-test providers on the basic use cases, 
and gives users an easy way to switch and test among different providers.

## Installation

Please ensure that you have **ffmpeg** installed before install USTTC.

You can install the module using Python Package Index using the command below.

    pip install usttc

## Create account on STT providers

Currently, USTTC supports the following 6 STT providers. We are going to include a few more providers later on.
* [Google Speech-to-Text](https://cloud.google.com/speech-to-text)
* [AWS Transcribe](https://aws.amazon.com/transcribe/)
* [Voicegain.ai](https://www.voicegain.ai/)
* [Rev.ai](https://www.rev.ai/)
* [assembly.ai](https://www.assemblyai.com/)
* [deepgram](https://deepgram.com/)

We include these 6 providers, because all of them have comparable accuracy, 
reasonable complete features, and easy-to-use client SDKs. 
Now you need to decide which providers you want to test.
This is truly an overwhelming task, 
because there is no single right answer. 
Each provider has its own strengths and weaknesses on different audio characteristics, 
and also have different price strategy. 
If you don't know which one is the best for your application,
we suggest you should test all of them on your own audio samples to get a sense. 
Fortunately, USTTC makes it very easy to test multiple providers using (almost) the same code.

The following table shows the price of each provider, so that you can also choose based on your budget.

Provider Price Details<sup>[1]</sup> | $ per minute | Free Tier per month | Free Credits | Minimum per request charge<sup>[4]</sup> | Increments
---------------------- | -------------| ------------------- | ------------ | -------------------------- | ----------
[Google Speech-to-Text](https://cloud.google.com/speech-to-text/pricing) | $0.0360 | 60 minutes | 8,333 minutes ($300)<sup>[2]</sup> | 15 seconds | 15 seconds
[AWS Transcribe](https://aws.amazon.com/transcribe/pricing/) | $0.0240 | 60 minutes<sup>[3]</sup> | No | 15 seconds | 1 second
[Voicegain.ai](https://www.voicegain.ai/pricing) | $0.0095 | No | 5,263 minutes ($50) | 1 second | 1 second
[Rev.ai](https://www.rev.ai/pricing) | $0.0350 | No | 300 minutes | 15 seconds | 15 seconds
[Assembly.ai](https://www.assemblyai.com/pricing) | $0.0150 | 180 minutes | No | 1 second | 1 second
[Deepgram](https://deepgram.com/pricing/) | $0.0125 | No | 12,000 minutes ($150) | *Not clear* | *Not clear*

*[1]: Price might change. Please check the pricing page for each provider*</br>
*[2]: Google Cloud Free credits is shared among all cloud services, and is only for the first 3 months*</br>
*[3]: AWS Free Tier is only for the first 12 months*</br>
*[4]: You need to consider this if the average audio duration is shorter than 15s in your application*

Once you decide which providers to test, you can create account on them following the instructions below.

### Google STT
```
asr_client = AsrClientFactory.get_client_from_key_file(
    asr_provider=AsrProvider.GOOGLE,
    filename="<>"
)
```
### AWS Transcribe
```
AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.AMAZON_AWS,
    key="<>",
    aws_secret_access_key="<>",
    region_name='<>'
)
```
### Voicegain.ai
```
AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.VOICEGAIN,
    key="<>"
)
```
### Rev.ai
```
AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.REV,
    key="<>"
)
```
### Assembly.ai
```
AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.ASSEMBLY_AI,
    key="<>"
)
```
### Deepgram
```
AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.DEEPGRAM,
    key="<>"
)
```

## Usage

### Transcribe Pre-Recorded Audio

```
audio = AudioFile(file_path=file)
result = asr_client.recognize(config, audio)
```
#### Diarization

#### Multi-Channel Audio

### Transcribe Audio Stream
Coming soon...
