import re


class StreamResult:
    def __init__(self, transcript, is_final):
        self.transcript = transcript.strip()
        self.is_final = is_final


class StreamResults:
    def __init__(self, responses):
        self.stream_result_list = []
        self.responses = responses

    def get_transcript(self):
        return " ".join(i.transcript for i in self.stream_result_list if i.is_final)

    def till_end(self):
        for response in self.responses:
            if not response.is_final:
                if self.stream_result_list and (not self.stream_result_list[-1].is_final) and \
                        (self.stream_result_list[-1].transcript == response.transcript):
                    continue
                print("MID: " + response.transcript)
                self.stream_result_list.append(response)
            else:
                self.stream_result_list.append(response)
                print("FIN: " + response.transcript)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r"\b(exit|quit)\b", response.transcript, re.I):
                    print("Exiting..")
                    break
