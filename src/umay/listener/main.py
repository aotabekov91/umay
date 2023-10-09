import json
from os import path
from plug import Plug
from threading import Thread
from vosk import Model, KaldiRecognizer
from speech_recognition import Recognizer, Microphone

class Listener(Plug):

    def __init__(
            self, 
            umay,
            *args,
            lan='en',
            **kwargs,
            ): 

        self.lan=lan
        self.umay=umay
        self.chunk=512
        self.pbar = .5
        self.nsd = .25
        self.ebar = 100
        super().__init__(*args, **kwargs)

    def setup(self):

        base_dir=path.dirname(
                path.realpath(__file__))
        self.model_dir=f'{base_dir}/model'
        super().setup()
        if path.exists(self.model_dir):
            self.setRecog()
            self.setVosk()
            self.setMicrophone()
        else:
            return "Please download the model"

    def setRecog(self):

        self.recog=Recognizer()
        self.recog.pause_threshold = self.pbar 
        self.recog.energy_threshold = self.ebar
        self.recog.non_speaking_duration = self.nsd 

    def setVosk(self):

        self.vosk_model = Model(
                self.model_dir)
        self.rec = KaldiRecognizer(
                self.vosk_model, 36000);

    def setMicrophone(self):

        try:
            self.mic=Microphone(self.chunk)
            with self.mic as m:
                self.recog.adjust_for_ambient_noise(m)
        except:
            self.mic=None
        
    def parse(self, adata, lan='en'):

        self.rec.AcceptWaveform(
                adata.get_raw_data(
                    convert_rate=36000, 
                    convert_width=2));
        return self.rec.FinalResult()
    
    def listen(self):

        def run():
            self.listening=True
            with self.mic as mic:
                while self.listening:
                    try: 
                        audio = self.recog.listen(
                                mic, 1, None)
                        self.handle(audio)
                    except Exception:  
                        pass

        if self.mic:
            thread=Thread(target=run)
            thread.deamon=True
            thread.start()
            return thread
        else:
            print('No microphone')

    def quit(self):

        self.listening=False
        print('Listener exiting')

    def handle(self, audio):

        parsed=self.parse(
                audio, self.lan)
        j=json.loads(parsed)
        if j['text']:
            self.umay.parse(j['text'])
