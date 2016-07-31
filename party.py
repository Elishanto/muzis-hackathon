import os
import pwd
import grp

from jinja2 import Environment, FileSystemLoader
from mpd import MPDClient
from random import randint
from time import sleep
from urllib.request import urlretrieve
from subprocess import call, Popen

PARTY_HOME = "/parties"
TEMPLATES_PATH = "./config_templates"
PARTY_HOST = "139.59.212.18"

ICECAST_PASS = 123
ICECAST_ORIG_PATH = "/etc/icecast2/"

class Party:

    def __init__(self, party_id, logger, songs):
        self.party_id = party_id
        self.songs = songs
        self.icecast2_port = randint(9100, 9500)
        self.party_port = self.icecast2_port + 10000

        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))

        self.__mk_party_dirs()
        self.__mk_icecast_xml()
        self.__mk_mpd_config()

        for s in songs:
            logger.info('Downloading song: ' % s)
            urlretrieve(s, os.path.join(self.music_dir, "test.mp3"))

        self.icecast_proc = Popen("icecast2 -b -c " + os.path.join(self.party_path, "icecast.xml"), shell = True)
        self.mpd_proc = Popen("mpd " + os.path.join(self.party_path, "mpd.conf"), shell = True)

        sleep(5)
        self.client = MPDClient()
        self.client.connect(PARTY_HOST, self.party_port)
        self.client.rescan()

        logger.info('Party "%s" initiated at port %s' % (self.party_id, self.icecast2_port))

    def __mk_party_dirs(self):
        self.party_path = os.path.join(PARTY_HOME, self.party_id)
        if not os.path.exists(self.party_path):
            os.makedirs(self.party_path)

        self.icecast2_path = os.path.join(self.party_path, "icecast2")
        if not os.path.exists(self.icecast2_path):
            os.makedirs(self.icecast2_path)
            for sub in ["log", "web", "admin"]:
                os.makedirs(os.path.join(self.icecast2_path, sub))
                call(['cp', '-r', os.path.join(ICECAST_ORIG_PATH, sub), self.icecast2_path])

        for sub in ["music", "playlists", "lib", "log"]:
            sub_path = os.path.join(self.party_path, sub)
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
            if sub == "music": self.music_dir = sub_path
            if sub == "lib":
                with open(os.path.join(sub_path, "tag_cache"), "wt") as _:
                    os.chmod(os.path.join(sub_path, "tag_cache"), 0o777)

        uid = pwd.getpwnam("icecast").pw_uid
        gid = grp.getgrnam("icecast").gr_gid
        os.chown(os.path.join(self.icecast2_path, "log", "access.log"), uid, gid)
        os.chown(os.path.join(self.icecast2_path, "log", "error.log"), uid, gid)

        with open(os.path.join(self.party_path, "pid"), "wt") as _:
            os.chmod(os.path.join(self.party_path, "pid"), 0o777)

    def __mk_icecast_xml(self):
        ice_template = self.jinja_env.get_template('icecast.xml')
        ice_xml = ice_template.render(
            party_home=PARTY_HOME,
            party_id=self.party_id,
            party_port=self.party_port,
            icecast_port=self.icecast2_port,
            icecast_pass=ICECAST_PASS
        )

        ice_file_path = os.path.join(self.party_path, "icecast.xml")
        with open(os.path.join(self.party_path, "icecast.xml"), "w") as ice_file:
            ice_file.write(ice_xml)
        call(['chown', '-R', 'icecast:icecast', ice_file_path])

    def __mk_mpd_config(self):
        """
        Create config file to run MPD to control the party
        :return: None
        """
        mpd_template = self.jinja_env.get_template('mpd.conf')
        mpd_conf = mpd_template.render(
            party_home=PARTY_HOME,
            party_id=self.party_id,
            party_port=self.party_port,
            icecast_port=self.icecast2_port,
            icecast_pass=ICECAST_PASS
        )
        with open(os.path.join(self.party_path, "mpd.conf"), "w") as mpd_file:
            mpd_file.write(mpd_conf)

    def get_stream_url(self):
        return "http://%s:%s/%s" % (PARTY_HOST, self.party_port, self.party_id)

    def start(self):
        self.client.play()

    def next(self):
        self.client.next()

    def stop_party(self):
        self.icecast_proc.kill()
        self.mpd_proc.kill()

if __name__ == "__main__":
    test_party = Party("userVasya_party23", ["http://www.stephaniequinn.com/Music/Vivaldi%20-%20Spring%20from%20Four%20Seasons.mp3"])