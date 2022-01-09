# USTTC (Unified Speech-to-Text Client)

This project provides a simple and unified client wrapper for multiple [Speech-to-test (STT)](https://en.wikipedia.org/wiki/Speech_recognition) providers on the basic use cases, 
and gives users an easy way to switch and test among different providers.

## Background
The accuracy of Speech-to-text (STT) improved significantly during the past few years. 
There are a lot of cloud STT providers on the market, 
including some big players like Google and AWS, 
and a few ambitious new providers like Voicegain.ai and Assembly.ai. 

As a Speech Recognition Scientist, I have reviewed many providers in the last few years, 
and I have noticed that each provider has its unique features. 
However, most users do not necessarily need those additional features, 
especially in the early testing stage. 
Their requirements are very simple and basic -- getting accurate transcript of the provided audio.

In terms of my personal background, I am the Senior AI Scientist in Voicegain (specializing in Speech Recognition), 
but USTTC is a personal project, and I try to do it without any bias. 
As mentioned, the goal of this project is to enable more people in the community to explore and test STT 
without too much trouble of dealing with varied providers, APIs and documentations. 


## Installation

Please ensure that you have **ffmpeg** installed before install USTTC.

You can install the module using Python Package Index using the command below.

    pip install usttc

## Determine which STT providers to test
Currently, USTTC supports the following 6 STT providers. We are going to include a few more providers later on.
* [Google STT](https://cloud.google.com/speech-to-text)
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

Provider Price Details<sup>[1]</sup> | $ per minute<sup>[2]</sup> | Free Tier per month | Free Credits | Minimum per request charge<sup>[3]</sup> | Increments
---------------------- | -------------| ------------------- | ------------ | -------------------------- | ----------
[Google STT](https://cloud.google.com/speech-to-text/pricing) | $0.0360 | 60 minutes | 8,333 minutes ($300)<sup>[4]</sup> | 15 seconds | 15 seconds
[AWS Transcribe](https://aws.amazon.com/transcribe/pricing/) | $0.0240 | 60 minutes<sup>[5]</sup> | No | 15 seconds | 1 second
[Voicegain.ai](https://www.voicegain.ai/pricing) | $0.0095 | No | 5,263 minutes ($50) | 1 second | 1 second
[Rev.ai](https://www.rev.ai/pricing) | $0.0350 | No | 300 minutes | 15 seconds | 15 seconds
[Assembly.ai](https://www.assemblyai.com/pricing) | $0.0150 | 180 minutes | No | 1 second | 1 second
[Deepgram](https://deepgram.com/pricing/) | $0.0125 | No | 12,000 minutes ($150) | *Not clear* | *Not clear*

*[1]: Price might change. Please check the pricing page for each provider*</br>
*[2]: This is the pay-as-you-go price. All providers provide discount for high volumes*</br>
*[3]: You need to consider this if the average audio duration is shorter than 15s in your application*</br>
*[4]: Google Cloud Free credits is shared among all cloud services, and is only for the first 90 days*</br>
*[5]: AWS Free Tier is only for the first 12 months*

## Create account on selected STT providers
Once you decide which providers to test, you can create account on them following the steps below.

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

You can use USTTC to transcribe both pre-recorded audio file, or real-time audio stream.

### Transcribe Pre-Recorded Audio
Using USTTC, it's super easy to transcribe your audio file in (almost) **any format**.
```
from usttc.audio import AudioFile

audio = AudioFile(file_path="<YOUR_AUDIO_FILE_PATH>")
result = asr_client.recognize(audio)
print(result.transcript)
```
#### Diarization
*Coming soon*
#### Multi-Channel Audio
*Coming soon*

### Ensemble
*This feature will be available soon*

### Compare transcription result
*This feature will be available soon*

### Transcribe Audio Stream
*This feature will be available soon*
