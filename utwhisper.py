
import urllib2
import re
import json
import sys
import settings

class Torrent:

    def __set_opener(self):
        """ returns an opener with url, user, passwd """
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='uTorrent', uri=settings.WEBUI, user=settings.USER, passwd=settings.PASSWD)
        opener = urllib2.build_opener(auth_handler)
        return opener
    
    def __token(self):
        """
        extract token and cookie
        """

        opener = self.__set_opener()
        urllib2.install_opener(opener)
        token_location = settings.WEBUI + 'token.html'
        
        # open token location
        try:
            response = urllib2.urlopen(token_location)
        except:
            print "[error]: error opening token page.\nCheck your settings at settings.py.\nexiting."
            sys.exit(0)
            # exit
            

        # get cookie
        cookie = response.headers['Set-Cookie']
        #print "[dbg] Cookie ... " + cookie
        
        response = response.read()

        # extract token
        token = re.compile('>([^<]+)<')
        matches = re.search(token, response)
        token = matches.group(0)[1:-1]
        #print "[dbg] Token ... " + token

        # save token & cookie for reuse.
        authreuse = open(settings.AUTH_SAVE_PATH, "w")
        authreuse.write(token + "%" + cookie)
        authreuse.close()
        
        return (token, cookie)
    
    def __request(self, action):
        """
        all API actions goes thru this method.
        each action must start with &.
        """

        opener = self.__set_opener()

        # try to load previous token & cookie
        try:
            authreuse = open(settings.AUTH_SAVE_PATH, "r")
            token, cookie = authreuse.read().split("%")
            print "[dbg]: reusing:\nToken: {0}\nCookie: {1}\n".format(token, cookie)
        except:
            # token or cookie not reusable, requesting new
            print "[dbg]: request new token, cookie"
            (token, cookie) = self.__token()
        
        # since every request needs a cookie, put it into header.
        opener.addheaders = [('Cookie', cookie)]
        urllib2.install_opener(opener)
    
        target = settings.WEBUI + "?token=" + token + action
        print "[dbg] Request ... " + target

        try:
            response = urllib2.urlopen(target)
        except:
            print "[error]: error opening {0}\nCleaning auth data at{1}. Try again now.\nexiting.".format(target, settings.AUTH_SAVE_PATH)
            authreuse = open(settings.AUTH_SAVE_PATH, "w")
            authreuse.close()
            sys.exit(0)
            # exit
                                                                                 
        # we got json
        data = response.read()
        print "[dbg] Data size: %s\n" % (len(data))
        return data

    def hashtable(self):
        """ prints for each torrent it's hash, index and name """
        torrents = json.loads(self.__request("&list=1"))['torrents']
        index = 0
        for each in torrents:
                print "{0} -> {1} -> {2}\n".format(index, each[0], each[2])
                index += 1

    def index2hash(self, index):
        """ get torrent index and return torrent hash """
        print "[dbg]: input: " + str(index)
        return json.loads(self.__request("&list=1"))['torrents'][index][0]


##### API ######
    def torrents_list(self):
        """ API: list=1 """
        #print self.__request("&list=1")
        torrents = json.loads(self.__request("&list=1"))['torrents']
        torrent_props = TorrentProperties(torrents)
        torrent_props.print_all()

    def getsettings(self):
        """ API: action=getsettings """
        print self.__request("&action=getsettings")
        
    def getfiles(self, options):
        """ API: action=getfiles&hash=[TORRENT HASH] """
        print '[dbg]: getfiles -> ' + str(options)
        torrent_index = int(options[0])
        files_json = json.loads(self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index)))
        files = TorrentFiles(files_json)
        files.print_files()
        #return self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index))

    def setsettings(self, options):
        """
        API:
            change setting: action=setsetting&s=[SETTING]&v=[VALUE]
            change _multiple_ settings: action=setsetting&s=[SETTING]&v=[VALUE]&s=[SETTING_2]&v=[VALUE_2]
            ex: action=setsetting&s=max_ul_rate&v=10&s=max_dl_rate&v=40
            Instead of False\True use 0\1.
        """
        settings = re.sub('\s+', '', options[0])

        req = '&action=setsetting'
        splitted = settings.split('&')
        for opts in splitted:
            try:
                (setting, value) = opts.split('=')
            except:
                print "[Error]: Failed to parse `{0}`".format(options[0])
                return 0
            req += "&s=" + setting + "&v=" + value

        self.__request(req)

    
    def torrentprops(self, options):
        """ API:  action=getprops&hash=[TORRENT HASH] """
        #print self.__request("&action=getprops&hash=" + self.index2hash(torrent_index))
        #props_json = json.loads(self.__request("&action=getprops&hash=" + self.index2hash(torrent_index)))['props']
        torrent_index = int(options[0])
        props_dict = json.loads(self.__request("&action=getprops&hash=" + self.index2hash(torrent_index)))['props'][0]
        props = TorrentJob(props_dict)
        props.print_props()

    def start(self, options):
        """ API: action=start&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=start&hash=" + self.index2hash(torrent_index))

    def stop(self, options):
        """ API: action=stop&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=stop&hash=" + self.index2hash(torrent_index))

    def pause(self, options):
        """ API: action=pause&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=pause&hash=" + self.index2hash(torrent_index))

    def forcestart(self, options):
        """ API: action=forcestart&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=forcestart&hash=" + self.index2hash(torrent_index))

    def unpause(self, options):
        """ API: action=unpause&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=unpause&hash=" + self.index2hash(torrent_index))

    def recheck(self, options):
        """ API: action=recheck&hash=[TORRENT HASH]  """
        torrent_index = int(options[0])
        print self.__request("&action=recheck&hash=" + self.index2hash(torrent_index))

    def remove(self, options):
        """ API: action=remove&hash=[TORRENT HASH]  """
        torrent_index = int(options[0])
        print self.__request("&action=remove&hash=" + self.index2hash(torrent_index))

    def removedata(self, options):
        """ API: action=removedata&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=removedata&hash=" + self.index2hash(torrent_index))

    def removetorrent(self, options):
        """ API: action=removetorrent&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=removetorrent&hash=" + self.index2hash(torrent_index))

    def removedatatorrent(self, options):
        """ API: action=removedatatorrent&hash=[TORRENT HASH] """
        torrent_index = int(options[0])
        print self.__request("&action=removedatatorrent&hash=" + self.index2hash(torrent_index))

    def setprio(self, options):
        """
        options: torrent_index, priority, file_index

        API: action=setprio&hash=[TORRENTHASH]&p=[PRIORITY]&f=[FILE INDEX]
        0 = Don't Download
        1 = Low Priority
        2 = Normal Priority
        3 = High Priority
        """

        torrent_index = int(options[0])
        priority = int(options[1])
        file_index = int(options[2])
        
        print self.__request("&action=setprio&hash=" + self.index2hash(torrent_index)
                       + "&p=" + str(priority) + "&f=" + str(file_index))

    def getxferhist(self):
        """ API: action=getxferhist """
        print self.__request("&action=getxferhist")

    def resetxferhist(self):
        """ API: action=resetxferhist  """
        print self.__request("&action=resetxferhist")

    def getversion(self):
        """ API: action=getversion """
        print self.__request("&action=getversion")

    def addurl(self, options):
        """ 
        options: torrent_url, download_dir=0, path=''

        API: action=add-url&s=[TORRENT URL]
        
        Optional:
            &download_dir=<integer>
            &path=<sub_path>
        """

        
        torrent_url = options[0]

        try:
            download_dir = int(options[1])
        except:
            download_dir = 0

        try:
            path = options[2]
        except:
            path = ''
    
        addurl_req = "&action=add-url&s=" + torrent_url
        
        # optional parameters
        if download_dir > 0:
            addurl_req += "&download_dir=" + str(download_dir)
        if path != '':
            addurl_req += "&path=" + path
            
        print self.__request(addurl_req)

    def addfile(self):
        """
        # NOT IMPLEMENTED. have issues with that one.
        # helpful: http://www.doughellmann.com/PyMOTW/urllib2/
        
        API: action=add-file
        """
        print "Sorry, not implemented. See README for workaround."
        pass

    def listdirs(self):
        """ API: action=list-dirs """
        #action=list-dirs
        
        dir_list = json.loads(self.__request("&action=list-dirs"))["download-dirs"]

        index = 0
        for each in dir_list:
            print "index: {0}".format(index)
            print "path: {:>4}".format(each['path'])
            print "free: {:>4}\n".format(each['available'])
            
            index += 1

##### ENDOF API ######
            
    def request(self, options):
        """
        pass your own request.
        look at utorrent server documentation for all available actions.
        """

        action = "&action=" + options[0]
        print self.__request(action)
                


class TorrentProperties:
        """
        This class contains all properties for all torrents.

        TODO: some properties contain values in bytes.
                convert them to mb, kb/s and etc.
                damn, it's so boring task.

        data stucture: [
                        {'hash': '123..', 'name': 'torrent 1'},
                        {'hash': '351..', 'name': 'torrent 2'
                        ]
                        
        """
        
        def __init__(self, torrents_json):
                self.torrents = []
                for each in torrents_json:
                        self.torrents.append(
                                {
                                'hash': each[0],
                                'status': each[1],
                                'name': each[2],
                                'size': each[3],
                                'percent progress': each[4],
                                'downloaded': each[5],
                                'uploaded': each[6],
                                'ratio': each[7],
                                'upload speed': each[8],
                                'download speed': each[9],
                                'eta': each[10],
                                'label': each[11],
                                'peers connected': each[12],
                                'peers in swarm': each[13],
                                'seeds connected': each[14],
                                'availability': each[15],
                                'torrent queue order': each[16],
                                'remaining': each[17],
                                'download url': each[18],
                                'rss feed url': each[19],
                                'status message': each[20],
                                'stream id': each[21],
                                'added on': each[22],
                                'completed on': each[23],
                                'app update url': each[24]
                                 }
                                )
        def print_all(self):
                """
                prints all torrents.
                adjust this method output for your needs.
                """
                index = 0
                for each in self.torrents:
                        print """
index: {0}
name: {1}
size: {2}
completed: {3}
""".format(index, each['name'], each['size'], each['percent progress'])
                        index += 1
                        

class TorrentFiles:
        """
        Class contains properties for torrent files.
        """
        def __init__(self, files_json):
                  self.files  = []
                  self.thash = files_json['files'][0]
                  for each in files_json['files'][1]:
                          self.files.append(
                                  {
                                          'filename': each[0],
                                          'filesize': each[1],
                                          'downloaded': each[2],
                                          'priority': each[3],
                                          'first piece': each[4],
                                          'num pieces': each[5],
                                          'streamable': each[6],
                                          'encoded rate': each[7],
                                          'duration': each[8],
                                          'width': each[9],
                                          'height': each[10],
                                          'stream eta': each[11],
                                          'streamability': each[12]
                                          }
                                  )
        def print_files(self):
                """ print all files of this torrent """

                print "hash: " + self.thash
                for each in self.files:
                        print """
file: %s
size: %s
downloaded: %s
priority: %s
""" % (each['filename'], each['filesize'], each['downloaded'], each['priority'])



class TorrentJob:
        """
        Class contains properties for torrent job.
        """

        def __init__(self, props_dict):
                self.props = {}
                self.props = props_dict

        def print_props(self):
                """ print torrent job properties """
                print self.props['hash']
                print self.props['trackers']
                
                # and etc.

    

class Executer:

    # preffered command name -> method name (of Torrent class)


    # parser
    def __init__(self, console_input):
        self.command = ''
        self.options = []
        self.aliases = {
            'torrentslist': 'torrents_list',
            'getsettings': 'getsettings',
            'getfiles': 'getfiles',
            'setsettings': 'setsettings',
            'torrentprops': 'torrentprops',
            'start': 'start',
            'stop': 'stop',
            'pause': 'pause',
            'forcestart': 'forcestart',
            'unpause': 'unpause',
            'recheck': 'recheck',
            'remove': 'remove',
            'removedata': 'removedata',
            'removetorrent': 'removetorrent',
            'removedatatorrent': 'removedatatorrent',
            'setprio': 'setprio',
            'transferhistory': 'getxferhist',
            'resettranserhistory': 'resetxferhist',
            'getversion': 'getversion',
            'addurl': 'addurl',
            'addfile': 'addfile',
            'listdirs': 'listdirs',
            'request': 'request',
            'hashtable': 'hashtable'
        }

        print "[dbg]: console_input: " + str(console_input)

        try:    
            cmd = console_input[0]
        except:
            cmd = "[error]: no command was supplied. exiting."
            sys.exit(0)


        try:    
            options = console_input[1:]
        except:
            options = []

        
        cmd = re.sub(r'-+', '', cmd) # remove --, -
        self.command = cmd
        self.options = options

        print "[dbg]: exiting __init__"
        
    def execute_api(self):
        torrent = Torrent()

        print "[dbg]: executing: {0}".format(self.alias_of(self.command))
        call_method = getattr(torrent, self.alias_of(self.command))

        if len(self.options) > 0:
            call_method(self.options) # if options supplied, pass them.
        else:
            call_method() # otherwise, call method without any options


    def alias_of(self, command):
        return self.aliases[command]

    

args = sys.argv[1:]
ex = Executer(args)
ex.execute_api()
