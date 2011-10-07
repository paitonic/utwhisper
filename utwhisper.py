
import urllib2
import re
import json
import sys


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
                for each in self.torrents:
                        print """
name: %s
size: %s
percent: %s
""" % (each['name'], each['size'], each['percent progress'])
        
                        
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
        print self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index))

    def torrentprops(self, torrent_index):
        """ API:  action=getprops&hash=[TORRENT HASH] """
        print self.__request("&action=getprops&hash=" + self.index2hash(torrent_index))

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

    def setprio(self, torrent_index):
        """ API: action=setprio&hash=[TORRENTHASH]&p=[PRIORITY]&f=[FILE INDEX] """
        print self.__request("action=setprio&hash=[TORRENTHASH]&p=[PRIORITY]&f=[FILE INDEX]")

    def getxferhist(self):
        """ API: action=getxferhist """
        print self.__request("&action=getxferhist")

    def resetxferhist(self):
        """ API: action=resetxferhist  """
        print self.__request("&action=resetxferhist")

    def getversion(self):
        """ API: action=getversion """
        print self.__request("&action=getversion")

    def addurl(self, url):
        """ API: action=add-url&s=[TORRENT URL] """
        # optional
        # &download_dir=<integer>
        # &path=<sub_path>
        
        print self.__request("&action=add-url&s=" + torrent_url)

    def addfile(self):
        """ API: action=add-file """
        # action=add-file
        pass

    def listdirs(self):
        """ API: action=list-dirs """
        #action=list-dirs
        pass

