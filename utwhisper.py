
import urllib2
import re
import json
import sys

# TODO
# * addfile method. laziness.
# * at TorrentFiles, TorrentJob, TorrentProperties some types need to
#       converted into more friendly-human format. i.e size of file from bytes to MB
# * refactoring.
# * arguments and options implementation is ugly.
# * add exception for stability.

# timeout error:
# urllib2.URLError: <urlopen error [Errno 10060] A connection attempt failed becau
# se the connected party did not properly respond after a period of time, or estab
# lished connection failed because connected host has failed to respond>
                

class Torrent:
    
    def __init__(self):
        self.webui = 'http://10.0.0.3:8081/gui/'
        self.username = 'root'
        self.passwd = 'torrent'
    
        
    def __auth(self):
        """
                extracts token and cookie.
        """
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='uTorrent', uri=self.webui, user=self.username, passwd=self.passwd)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        token_location = self.webui + 'token.html'
        response = urllib2.urlopen(token_location)
    
        cookie = response.headers['Set-Cookie'] # cookie
        #print "[dbg] Cookie ... " + cookie # DEBUG
        response = response.read()
    
        token = re.compile('>([^<]+)<')
        matches = re.search(token, response)
        token = matches.group(0)[1:-1] # token
        #print "[dbg] Token ... " + token # DEBUG
        
        return (token, cookie)
    
    def __request(self, action):
        """
                all API actions goes thru this method.
        each action must start with &.
        """
        
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='uTorrent', uri=self.webui, user=self.username, passwd=self.passwd)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
    
        (token, cookie) = self.__auth() # authentication
        opener.addheaders = [('Cookie', cookie)] # put the cookie from auth() in header.
        urllib2.install_opener(opener)
    
        target = self.webui + "?token=" + token + action
        
        print "[dbg] Request ... " + target # DEBUG
        response = urllib2.urlopen(target)
        data = response.read()
        print "[dbg] Data size: %s" % (len(data)) # DEBUG
        return data

    def hashtable(self):
        """ print table index->torrent hash->torrent name """
        torrents = json.loads(self.__request("&list=1"))['torrents']
        index = 0
        for each in torrents:
                # index, each[0]->torrent hash, each[2]->torrent name
                print "%s -> %s -> %s\n" % (index, each[0], each[2])
                index += 1

    def index2hash(self, index):
        """ get torrent index and return torrent hash """
        # return self.torrent_index[index]
        return json.loads(self.__request("&list=1"))['torrents'][index][0]


        # actions
    def torrents_list(self):
        """
        API: list=1 
        """
        #print self.__request("&list=1")
        torrents = json.loads(self.__request("&list=1"))['torrents']
        torrent_props = TorrentProperties(torrents)
        torrent_props.print_all()

    def getsettings(self):
        """ API: action=getsettings """
        print self.__request("&action=getsettings")

    def getfiles(self, torrent_index):
        """ API: action=getfiles&hash=[TORRENT HASH] """

        files_json = json.loads(self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index)))
        files = TorrentFiles(files_json)
        files.print_files()
        #return self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index))

    def torrentprops(self, torrent_index):
        """ API:  action=getprops&hash=[TORRENT HASH] """
        #print self.__request("&action=getprops&hash=" + self.index2hash(torrent_index))
        #props_json = json.loads(self.__request("&action=getprops&hash=" + self.index2hash(torrent_index)))['props']
        props_dict = json.loads(self.__request("&action=getprops&hash=" + self.index2hash(torrent_index)))['props'][0]
        props = TorrentJob(props_dict)
        props.print_props()

    def start(self, torrent_index):
        """ API: action=start&hash=[TORRENT HASH] """
        print self.__request("&action=start&hash=" + self.index2hash(torrent_index))

    def stop(self, torrent_index):
        """ API: action=stop&hash=[TORRENT HASH] """
        print self.__request("&action=stop&hash=" + self.index2hash(torrent_index))

    def pause(self, torrent_index):
        """ API: action=pause&hash=[TORRENT HASH] """
        print self.__request("&action=pause&hash=" + self.index2hash(torrent_index))

    def forcestart(self, torrent_index):
        """ API: action=forcestart&hash=[TORRENT HASH] """
        print self.__request("&action=forcestart&hash=" + self.index2hash(torrent_index))

    def unpause(self, torrent_index):
        """ API: action=unpause&hash=[TORRENT HASH] """
        print self.__request("&action=unpause&hash=" + self.index2hash(torrent_index))

    def recheck(self, torrent_index):
        """ API: action=recheck&hash=[TORRENT HASH]  """
        print self.__request("&action=recheck&hash=" + self.index2hash(torrent_index))

    def remove(self, torrent_index):
        """ API: action=remove&hash=[TORRENT HASH]  """
        print self.__request("&action=remove&hash=" + self.index2hash(torrent_index))

    def removedata(self, torrent_index):
        """ API: action=removedata&hash=[TORRENT HASH] """
        print self.__request("&action=removedata&hash=" + self.index2hash(torrent_index))

    def removetorrent(self, torrent_index):
        """ API: action=removetorrent&hash=[TORRENT HASH] """
        print self.__request("&action=removetorrent&hash=" + self.index2hash(torrent_index))

    def removedatatorrent(self, torrent_index):
        """ API: action=removedatatorrent&hash=[TORRENT HASH] """
        print self.__request("&action=removedatatorrent&hash=" + self.index2hash(torrent_index))

    def setprio(self, torrent_index, priority, file_index):
        """
        API: action=setprio&hash=[TORRENTHASH]&p=[PRIORITY]&f=[FILE INDEX]
        0 = Don't Download
        1 = Low Priority
        2 = Normal Priority
        3 = High Priority
        """
        #print self.__request("action=setprio&hash=[TORRENTHASH]&p=[PRIORITY]&f=[FILE INDEX]")
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

    def addurl(self, torrent_url):
        """ API: action=add-url&s=[TORRENT URL] """
        # optional
        # &download_dir=<integer>
        # &path=<sub_path>
        
        print self.__request("&action=add-url&s=" + torrent_url)

    def addfile(self):
        # TODO
        # lazy to implement this.
        # http://www.doughellmann.com/PyMOTW/urllib2/
        """ API: action=add-file """
        # action=add-file
        pass

    def listdirs(self):
        """ API: action=list-dirs """
        #action=list-dirs
        pass



    def request(self, action):
        """
        pass your own request
        """
        pass



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
index: %s
name: %s
size: %s
completed: %s
""" % (index, each['name'], each['size'], each['percent progress'])
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


# handle arguments and options.

args = sys.argv[1:]
torrent = Torrent()

if '--hashtable' in args:
        torrent.hashtable()
        
elif '--indextohash' in args:
        torrent.index2hash(args[2])
        
elif '--torrents-list' in args:
        torrent.torrents_list()
        
elif '--get-settings' in args:
        torrent.getsettings()
        
elif '--get-files' in args:
        torrent.getfiles(args[2])
        
elif '--torrent-props' in args:
        torrent.torrentprops(args[2])

elif '--start' in args:
        torrent.start(args[2])
        
elif '--stop' in args:
        torrent.stop(args[2])
        
elif '--pause' in args:
        torrent.pause(args[2])
        
elif '--force-start' in args:
        torrent.forcestart(args[2])
        
elif '--unpause' in args:
        torrent.unpause(args[2])
        
elif '--recheck' in args:
        torrent.recheck(args[2])
        
elif '--remove' in args:
        torrent.remove(args[2])
        
elif '--remove-data' in args:
        torrent.removedata(args[2])
        
elif '--remove-torrent' in args:
        torrent.removetorrent(args[2])
        
elif '--remove-data-torrent' in args:
        torrent.removedatatorrent(args[2])

elif '--set-prio' in args:
        torrent.setprio(args[2], args[3], args[4]) # torrent_index, priority, file_index
        
elif '--get-hist' in args:
        torrent.getxferhist()
        
elif '--reset-hist' in args:
        torrent.resetxferhist()
        
elif '--get-version' in args:
        torrent.getversion()
        
elif '--add-url' in args:
        torrent.addurl(args[2])
        
elif '--list-dirs' in args:
        torrent.listdirs()
        
elif '--req' in args:
        torrent.request(args[2])
        
