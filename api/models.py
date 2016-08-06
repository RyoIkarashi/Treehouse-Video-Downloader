import json


class Model:
    @classmethod
    def from_json_list(cls, data):
        return [cls.from_json(model) for model in data]


class Topic(Model):

    """ programming topics offered by teamtreehouse"""

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, data):
        if 'description' not in data:
            data['description'] = ''

        return cls(data['id'], data['name'], data['description'])


class Tracks(Model):

    """ tracks, i.e android development, web dev..."""

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

    @classmethod
    def from_json(cls, data):
        return cls(data['id'], data['title'], data['description'])


class Syllabi(Model):

    """ The content of a course. 1 syllabi has 1..* topics & stages """

    def __init__(self, id, title, description, topics, stages):
        self.id = id
        self.title = title
        self.description = description
        self.topics = topics
        self.stages = stages

    @classmethod
    def from_json(cls, data):
        return cls(data['id'], data['title'], data['description'],
            Topic.from_json_list(data['topics']),
            Stage.from_json_list(data['stages']))


class Stage(Model):

    """ A subset of the content for a course. i.e. 'getting start in x topic'
        Each stage has 1..* steps, these are either a video, quiz or programming
        test.
    """

    def __init__(self, id, title, description, order_index, steps = None):
        self.id = id
        self.title = title
        self.description = description
        self.order_index = order_index
        self.steps = steps

    @classmethod
    def from_json(cls, data):
        if 'steps' not in data:
            data['steps'] = []

        return cls(data['id'], data['title'], data['description'],
            data['order_index'], Step.from_json_list(data['steps']))

    def get_videos(self):
        return [s for s in self.steps if type(s) is VideoStep]

    def get_quizzes(self):
        return [s for s in self.steps if type(s) is QuizStep]

    def get_code_challenges(self):
        return [s for s in self.steps if type(s) is CodeChallengeStep]


class Step(Model):

    """ Base model for a step. This contains the actual learning material """

    def __init__(self, id, order_index, title, description):
        self.id = id
        self.order_index = order_index
        self.title = title
        self.description = description

    @staticmethod
    def from_json(data):
        item = data['item']
        item_type = data['item_type'].lower()

        kwargs = {
            'id': item['id'],
            'order_index': data['order_index'],
            'title': item['title'],
            'description': item['description']
        }

        if item_type == 'video':
            return VideoStep(**kwargs)
        elif item_type == 'quiz':
            return QuizStep(**kwargs)
        elif item_type == 'codechallenge':
            return CodeChallengeStep(**kwargs)


class VideoStep(Step):
    def __init__(self, id, order_index, title, description, video = None):
        Step.__init__(self, id, order_index, title, description)
        self.video = video


class QuizStep(Step):
    def __init__(self, id, order_index, title, description, quiz = None):
        Step.__init__(self, id, order_index, title, description)
        self.quiz = quiz


class CodeChallengeStep(Step):
    def __init__(self, id, order_index, title, description, challenge = None):
        Step.__init__(self, id, order_index, title, description)
        self.challenge = challenge


class Video(Model):
    def __init__(self, id, title, description, source_urls):
        self.id = id
        self.title = title
        self.description = description
        self.source_urls = source_urls

    @classmethod
    def from_json(cls, data):
        return cls(data['id'], data['title'], data['description'], data['video_urls'])

    def low_res(self):
        return self.source_urls['low_resolution']

    def medium_res(self):
        return self.source_urls['medium_resolution']

    def high_res(self):
        return self.source_urls['high_resolution']

    def high_def_res(self):
        return self.source_urls['high_definition_resolution']
