import subprocess
import os
from api import TreeHouseClient, TreeHouseAPI
from common import Cache, Stack
from video import VideoDownloader
import getpass

# TODO: this is still pretty horrible. Pls no judge me on dis file. I wus lazy

client = TreeHouseClient(TreeHouseAPI())
downloader = VideoDownloader(client)
cache = Cache()
back_stack = Stack()

def new_menu(title = None):
    subprocess.call("clear")
    if title:
        print("-------- " + title + " --------")

def print_opts(opts):
    print("commands")
    for opt in opts:
        print("- " + opt)
    print("----------------")

def pick_menu(choice):
    print("menu called")
    subprocess.call("clear")
    choice = choice.lower()

    if choice == "":
        actions['main_menu']()
    else:
        try:
            actions[choice]()
        except (KeyError, IndexError):
            print("Invalid choice")
            actions['main_menu']()


def auth_menu():
    new_menu("Login")

    while not client.authenticated:
        email = input("email: ")
        password = getpass.getpass("password: ")

        if not client.login(email, password):
            print("Login attempt failed")

    print("Authenticated")

    main_menu()

def main_menu():
    new_menu("Main Menu")

    if not cache.get("topics"):
        cache.set("topics", client.get_topics())

    print("[1] View Topics")
    print("[2] View Tracks")
    print("[3] Set download directory")
    back_stack.push(main_menu)
    pick_menu(input(">> "))

def download_dir_menu():
    directory = os.path.abspath(input("Please enter the path: ").replace('"',''))


    if not os.path.exists(directory):
        confirm = input("Create " + directory +  " ? [y/n]")

        if confirm == 'y':
            os.makedirs(os.path.abspath(directory))

    downloader.update_cwd(directory)
    input("CWD:  " + '"' + directory + '"' +  "Press Any key to continue" )

    back_stack.pop()()



def topics_menu():
    back_stack.push(main_menu)

    topics = cache.get("topics")

    new_menu("Topics")
    print_opts([
        "'b' to go back",
        "1-{0}".format(len(topics)) + " to choose a topic",
    ])

    for i in range(0, len(topics)):
        print("{0}: {1}".format(i+1, topics[i].name))

    out = input(">> ")

    if out == 'b':
        back_stack.pop()()
    else:
        back_stack.push(topics_menu)
        choice = topics[int(out) - 1]
        syllabi_list(choice)



def syllabi_list(topic):
    syllabi = cache.get(topic.name)

    if not syllabi:
        syllabi = client.get_syllabi_by_topic(topic)
        cache.set(topic.name, syllabi)

    new_menu(topic.name)

    print_opts([
        "'b' to go back",
        "1-{0}".format(len(syllabi)) + " to choose a syllabus",
    ])

    for i in range(0, len(syllabi)):
        print("{0}: {1}".format(i+1, syllabi[i].title))

    out = input(">> ")

    if out == 'b':
        back_stack.pop()()
    else:
        back_stack.push(syllabi_list)
        choice = syllabi[int(out) - 1]
        cache.set('last_topic', topic)
        syllabi_detail(choice)



def syllabi_detail(_syllabi):
    syllabi = cache.get(_syllabi.id)

    if not syllabi:
        syllabi = client.get_syllabi_detail(_syllabi)
        cache.set(syllabi.id, syllabi)

    new_menu(_syllabi.topics[0].name + " > " + _syllabi.title)

    print_opts([
        "'b' to exit",
        "1-{0}".format(len(syllabi.stages)) + " to choose a stage",
        "'all' to download all stages"
    ])

    for i in range(0, len(syllabi.stages)):
        stage = syllabi.stages[i]
        print("stage {0}: {1}".format(i+1, stage.title))

    out = input(">> ")

    if out == 'b':
        back_stack.pop()(cache.get('last_topic'))
        return


    back_stack.push(syllabi_detail)
    cache.set('last_syllabi', _syllabi)

    if out == 'all':
        download_course(syllabi)
    else:
        choice = syllabi.stages[int(out) - 1]
        syllabi_detail_stages(syllabi, choice)


def syllabi_detail_stages(syllabi, _stage):
    new_menu(syllabi.topics[0].name + " > " + syllabi.title + " > " + _stage.title)

    stage = cache.get(_stage.id)

    if not stage:
        stage = _stage
        client.set_stage_videos(stage)
        cache.set(stage.id, stage)

    print_opts([
        "'b' to exit",
        "1-{0}".format(len(syllabi.stages)) + " to download a video",
        "'all' to download all videos"
    ])

    for i in range(0, len(stage.get_videos())):
        step = stage.steps[i]

        print("step [video] {0}: {1}".format(i+1, step.title))

    print("***Only video steps are included***\n")

    out = input(">> ")

    if out == 'b':
        back_stack.pop()(cache.get('last_syllabi'))

def download_course(syllabi):
    downloader.download_course(syllabi)

    back_stack.pop()(cache.get('last_syllabi'))

def download_stage():
    pass

def download_step():
    pass



def tracks_menu():
    pass

actions = {
    'main_menu': main_menu,
    '1': topics_menu,
    '2': tracks_menu,
    '3': download_dir_menu
}

if __name__ == "__main__":
    auth_menu()
