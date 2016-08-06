import os
import requests

class VideoDownloader:
    CHUNK_SIZE = 8192

    def __init__(self, client, root = os.getcwd()):
        self.root = root
        self.client = client



    def download(self, url, file_name):
        r = requests.get(url, stream = True)
        file_name = file_name.replace("/", " ")
        file_name = file_name + '.' + r.headers['content-type'].split('/')[1]

        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(self.CHUNK_SIZE):
                f.write(chunk)

        print('downloaded ', file_name)
        f.close()
        r.close()

    def download_course(self, syllabi):

        for stage in syllabi.stages:
            # get all of the source urls for the videos of a stage
            self.client.set_stage_videos(stage)

            cwd = self._make_path([
                "videos",
                syllabi.topics[0].name,
                syllabi.title,
                str(stage.order_index) + "-" + stage.title
            ])

            self._create_directories(cwd)
            self._update_cwd(cwd)

            for video_step in stage.get_videos():
                self.download(video_step.video.high_def_res(),
                    str(video_step.order_index) + "-" + video_step.title)

            self._to_root_dir()


    def download_stage(self, stage):
        pass

    def download_step(self, step):
        pass

    def _update_cwd(self, directory):
        os.chdir(directory)

    def _make_path(self, paths):
        return "".join([p.replace(" ", "-") + "/" for p in paths])

    def _create_directories(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _to_root_dir(self):
        os.chdir(self.root)
