# USTTC (Unified Speech-to-Text Client)

This project provides a simple and unified client wrapper 
for multiple [Speech-to-test (STT)](https://en.wikipedia.org/wiki/Speech_recognition) providers on the basic use cases, 
and gives users an easy way to switch and test among different providers.

## Background
The accuracy of Speech-to-text (STT) improved significantly during the past few years. 
There are a lot of cloud STT providers on the market, including some big players like Google and AWS, 
and a few ambitious new providers like Voicegain.ai and Assembly.ai.

As a Speech Recognition Scientist, I have reviewed many providers in the last few years, 
and I have noticed that each provider has its own unique features. 
However, the majority of users do not necessarily need those additional features, 
especially in the early testing stage. 
Their requirements are very simple and basic -- getting an accurate transcript of the provided audio.

Regarding my personal background, I am an Senior AI Scientist at Voicegain (specializing in Speech Recognition), 
but this repository, USTTC, is a personal project, and I intend to work on it without any bias. 
As mentioned, the goal of this project is to enable more people in the community to explore and test STT 
without too much trouble dealing with varied providers, APIs, and documentation. 


## Installation

Please ensure that you have **ffmpeg** installed before install USTTC.

You can install the module using the Python Package Index using the command below.

    pip install usttc

## Determine which STT providers to test
Currently, USTTC supports the following 6 STT providers. We are going to include a few more providers later on.
* [Google STT](https://cloud.google.com/speech-to-text)
* [AWS Transcribe](https://aws.amazon.com/transcribe/)
* [Voicegain.ai](https://www.voicegain.ai/)
* [Rev.ai](https://www.rev.ai/)
* [assembly.ai](https://www.assemblyai.com/)
* [deepgram](https://deepgram.com/)

These six providers are included because they all have comparable accuracy, 
reasonable complete features, and simple-to-use client SDKs. Now you need to decide which providers you want to test. 
This is truly an overwhelming task, because there is no single right answer. 
Each provider has unique strengths and weaknesses, as well as its own unique pricing strategy.
If you don't know which one is best for your application, 
we suggest you test all of them on your own audio samples to get a sense. Fortunately, 
USTTC makes it very easy to test multiple providers using (almost) the same code, 
which is also the original intention of USTTC.

The following table shows the price of each provider, so that you can also choose based on your budget.

Provider Price Details<sup>[1]</sup> | $ per minute<sup>[2]</sup> | Free Tier per month | Free Credits | Minimum per request charge<sup>[3]</sup> | Increments
---------------------- | -------------| ------------------- | ------------ | -------------------------- | ----------
[Google STT](https://cloud.google.com/speech-to-text/pricing) | $0.0360 | 60 minutes | 8,333 minutes ($300)<sup>[4]</sup> | 15 seconds | 15 seconds
[AWS Transcribe](https://aws.amazon.com/transcribe/pricing/) | $0.0240 | 60 minutes<sup>[5]</sup> | No | 15 seconds | 1 second
[Voicegain.ai](https://www.voicegain.ai/pricing) | $0.0095 | No | 5,263 minutes ($50) | 1 second | 1 second
[Rev.ai](https://www.rev.ai/pricing) | $0.0350 | No | 300 minutes | 15 seconds | 15 seconds
[Assembly.ai](https://www.assemblyai.com/pricing) | $0.0150 | 180 minutes | No | 1 second | 1 second
[Deepgram](https://deepgram.com/pricing/) | $0.0125 | No | 12,000 minutes ($150) | *Not clear* | *Not clear*

*[1]: The price may change. Please check the pricing page for each provider*</br>
*[2]: This is the pay-as-you-go price. All providers provide discounts for high volumes*</br>
*[3]: You need to consider this if the average audio duration is shorter than 15s in your application*</br>
*[4]: The Google Cloud Free credits are distributed across all cloud services and are only valid for the first 90 days*</br>
*[5]: The AWS Free Tier is only available for the first 12 months*

## Create account on selected STT providers
Once you decide which providers to test, you can create an account with them by following the steps below.

### Google STT
1. Sign up Google Cloud Platform. https://console.cloud.google.com/getting-started
2. Enable **Google Cloud Speech API**. https://cloud.google.com/endpoints/docs/openapi/enable-api
3. Create a storage bucket. You can use the default setting. https://cloud.google.com/storage/docs/creating-buckets
4. Create a service account. Add **Cloud Speech Client** and **Storage Object Admin** two roles. https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-console
5. Create new **JSON key** for the service account you created. https://cloud.google.com/iam/docs/creating-managing-service-account-keys
```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key_file(
    asr_provider=AsrProvider.GOOGLE,
    filename="<YOUR_GOOGLE_CLOUD_JSON_KEY_FILE_PATH>",
    google_storage_bucket="<YOUR_GOOGLE_STORAGE_BUCKET_NAME>"
)
```
### AWS Transcribe
1. Sign up for AWS. https://portal.aws.amazon.com/billing/signup#/start
2. Create a S3 bucket. You can use the default setting. Please take a note of the **region** of your S3 bucket. https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html
3. Create a **User Group**. Attach **AmazonS3FullAccess** and **AmazonTranscribeFullAccess** permission to the group. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups_create.html
4. Add a **User** to the created **User Group**. Get user's **access key ID** and **secret access key**. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console
```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.AMAZON_AWS,
    key="<YOUR_AWS_USER_ACCESS_KEY_ID>",
    aws_secret_access_key="<YOUR_AWS_USER_SECRET_ACCESS_KEY>",
    region_name='<YOUR_S3_BUCKET_REGION>',
    s3_bucket='<YOUR_S3_BUCKET_NAME>'
)
```
### Voicegain.ai
1. Sign up. https://console.voicegain.ai/signup
2. Generate **JWT Token**. https://support.voicegain.ai/hc/en-us/articles/360028023691-JWT-Authentication

```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.VOICEGAIN,
    key="<YOUR_VOICEGAIN_JWT_TOKEN>"
)
```
### Rev.ai
1. Sign up. https://www.rev.ai/auth/signup
2. Generate **Access Token**. https://www.rev.ai/access_token
```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.REV,
    key="<YOUR_REV_ACCESS_TOKEN>"
)
```
### Assembly.ai
1. Sign up. https://app.assemblyai.com/signup
2. Get **API Key** on your account page. https://app.assemblyai.com/account
```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.ASSEMBLY_AI,
    key="<YOUR_ASSEMBLY_AI_API_KEY>"
)
```
### Deepgram
1. Sign up. https://console.deepgram.com/signup
2. Create **API Key** from the dashboard
```
from usttc import AsrClientFactory, AsrProvider

asr_client = AsrClientFactory.get_client_from_key(
    asr_provider=AsrProvider.DEEPGRAM,
    key="<YOUR_DEEPGRAM_API_KEY>"
)
```

## Usage

Both pre-recorded audio files and real-time audio streams can be transcribed with USTTC.

### Transcribe Pre-Recorded Audio
Using USTTC, it's super easy to transcribe your audio file in (almost) **any format**. [Here](examples/transcribe_audio_file_basic.py) is an end-to-end example of an .wav audio as the input. 
```
from usttc.audio import AudioFile

audio = AudioFile(file_path="<YOUR_AUDIO_FILE_PATH>")
result = asr_client.recognize(audio)
print(result.transcript)
```


#### Multiple Speakers
An audio file can contain multiple speakers in two ways.
* Multi-channel audio: Each channel has one speaker. (We only support stereo audio). In this case, you need to configure **separate_speaker_per_channel** ([example](examples/transcribe_audio_file_multi_channel.py))
* Mono audio: All speakers are mixed on the same channel. In this case, you need to configure **diarization** ([example](examples/transcribe_audio_file_diarization.py))

Please note here:
1. If your audio is stereo but both channels have the same content, you should **NOT** configure **separate_speaker_per_channel**.
2. **DO NOT** use diarization if speakers are already separated by channel.

### Compare transcription results
To compare the results from multiple recognizers and know which one is more accurate for the application, I'll normally start by reviewing a few results and getting a sense of the weaknesses and strengths of each recognizer. Sometimes, after I see a few examples, I can easily tell for a specific project which recognizers work and which do not.

If you want to compare the results in a more scientific manner, you can prepare the gold standard reference and calculate **[Word Error Rate (WER)](https://en.wikipedia.org/wiki/Word_error_rate)** of the results from each STT provider. However, calculating WER is not trivial, because we don't want to penalize a recognizer if the difference (its result vs. the gold reference) is just the punctuation and capitalization. Moreover, for a digit, it's both acceptable no matter whether using digit-format or spelled-out format.


#### transcribe-compare package
[Voicegain.ai](https://www.voicegain.ai/) provides a python package called [transcribe-compare](https://pypi.org/project/transcribe-compare/) 
to help you calculate WER (and do more than that). 
It solves many issues when calculating WER, including punctuation, capitalization, and digits mentioned above.
You can install the module using the Python Package Index using the command below.

     pip install transcribe-compare

We provide a simple [example](examples/calculate_wer_using_transcribe_compare.py) of using **USTTC** and **transcribe-compare** together.
You can also check their [GitHub page](https://github.com/voicegain/transcription-compare) for more examples of advanced use cases.

### Ensemble
*[This feature will be available soon]*

After you compare the results from multiple recognizers, you might realize that none of them is perfect (it is a cold and brute reality). Different STT providers might make mistakes in different places. If your budget allows, you can run multiple recognizers at the same time and get higher accuracy by ensembling their results. This feature is on our roadmap.

### Transcribe Audio Stream
*[This feature will be available soon]*

In some applications (e.g. real-time), it's important to stream the audio to the recognizer
and get the result simultaneously. 
All the STT providers that USTTC selected have the streaming feature. 
The streaming wrapper will be available soon.