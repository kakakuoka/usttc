# asr-bridger

[This project is in progress]

The accuracy of Speech-to-test (STT) improved significantly during the past few years. There are a lot of cloud STT providers on the market, including some big players like Google, AWS and Microsoft Azure, and a few ambitious new providers like Voicegain and Deepgram. 

As a Speech Recognition Scientist, I have reviewed many providers in the last few years, and I have noticed that each provider has its unique features. However, more than 95% of the users do not necessarily need those additional features, especially in the early stage. Their requirements are very simple and basic -- getting transcript of the provided audio. 

The intent of this open-sourced project is to provide a simple and generic wrapper for different STT providers on the most basic use cases, and to provide users with a easy way to switch and test among different providers. Based on my experience, there are generally two widely-applied use cases, and the wrapper will provide the methods to solve the corresponding use cases for almost all TTS cloud providers on the market. The two use cases are as follows:

1. Transcribe pre-recorded audio.
2. Transcribe audio stream.

In terms of my personal background, I am the Senior AI Scientist in Voicegain (specializing in Speech Recognition), but I wrote this personal project without any bias. As mentioned, the goal of this project is to enable more people in the community to explore STT without too much trouble of dealing with varied providers, APIs and documentations. 