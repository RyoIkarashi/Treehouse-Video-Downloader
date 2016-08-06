from .models import Topic, Syllabi, Video, VideoStep
from .helpers import bridge_method

class TreeHouseClient:
    def __init__(self, treehouse_api):
        self._treehouse_api = treehouse_api
        self.authenticated = False

    @bridge_method
    def login(self, username, password):
        """ authenticates with teamtreehouse """
        self.authenticated = self._treehouse_api.login(username, password)

        return self.authenticated

    @bridge_method
    def get_syllabi(self):
        """ Returns every course offered by teamtreehouse """
        syllabi = self._treehouse_api.get_syllabi()

        if syllabi:
            return Syllabi.from_json_list(syllabi)

    @bridge_method
    def get_syllabi_by_id(self, id):
        """ Returns the detail of a course with all stages & steps """
        syllabi = self._treehouse_api.get_syllabi_by_id(id)

        if syllabi:
            return Syllabi.from_json(syllabi)

    @bridge_method
    def get_topics(self):
        """ Returns the different topics teamtreehouse offers courses on """
        topics = self._treehouse_api.get_topics()

        if topics:
            return Topic.from_json_list(topics)

    @bridge_method
    def get_video(self, id):
        """ Returns the set of source URLs (low, med, high, vHigh) for a video """
        video = self._treehouse_api.get_video(id)

        if video:
            return Video.from_json(video)

    def get_syllabi_by_topic(self, topic):
        """ filters teamtreehouse's library by topic """
        topics = self.get_syllabi()

        return list(filter(lambda t: topic.name in
            list(map(lambda t: t.name, t.topics)), topics))

    def get_syllabi_detail(self, syllabi):
        """ returns full details for a course, i.e. all stages and steps """
        return self.get_syllabi_by_id(syllabi.id)

    def set_stage_videos(self, stage):
        """ Requests all the videos for a stage and updates the stage model """
        for step in stage.steps:
            if type(step) is VideoStep:
                step.video = self.get_video(step.id)
