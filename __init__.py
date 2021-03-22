import os

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from adapt.intent import IntentBuilder
from mycroft.audio import wait_while_speaking
from mycroft.util.parse import match_one


class LocalMusicPlayer(CommonPlaySkill):
    def __init__(self):
        """
        Initializes the playing variable.
        """
        super(LocalMusicPlayer, self).__init__(name="LocalMusicPlayer")
        self.playing = False

    def initialize(self):
        pause_audio = IntentBuilder("pause_audio").require("pause_audio").optionally("Neon").build()
        self.register_intent(pause_audio, self.handle_pause_intent)

        resume_audio = IntentBuilder("resume_audio").require("resume_audio").optionally("Neon").build()
        self.register_intent(resume_audio, self.handle_resume_intent)

    def CPS_match_query_phrase(self, phrase, message):
        """
        This method is invoked by PlayBackControlSkill.
        returns: tuple ((str) matched phrase,
                        CPSMatchLevel,
                        (dict) optional data)
                 or None if no match found.
        """
        music_dir = os.path.join(os.path.expanduser("~"), "Music")
        audio_files = os.listdir(music_dir)
        audio_dict = {}
        for file in audio_files:
            clean_file_name = file.split(".")[0].replace("_", " ")
            audio_dict[clean_file_name] = os.path.join(music_dir, file)
        match, confidence = match_one(phrase, audio_dict)
        if confidence > 0.5:
            return match, CPSMatchLevel.EXACT, {"track": match}
        else:
            return None

    def CPS_start(self, phrase, data, message):
        """
        Starts playback.
        Called if this skill has best match.
        """
        self.stop()
        url = data['track']
        self.audioservice.play(url)
        self.playing = True

    def handle_pause_intent(self):
        if self.playing:
            self.audioservice.pause()
            self.speak_dialog("PauseAudio")
            self.playing = False

    def handle_resume_intent(self):
        if not self.playing:
            self.speak_dialog("ResumeAudio")
            wait_while_speaking()
            self.audioservice.resume()
            self.playing = True

    def stop(self):
        """
        This skill handles stop if a track is playing.
        """
        if self.playing:
            self.audioservice.stop()
            self.playing = False


def create_skill():
    return LocalMusicPlayer()
