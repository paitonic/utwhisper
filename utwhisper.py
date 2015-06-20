
"""
Usage: utwhisper.py --[COMMAND] [OPTIONS]
	options marked [*OPTIONS] are not mandatory.
	examples: utwhisper.py
				--hashtable
				--addurl http://thepiratebay.org/torrent

Commands:
--help -- print this

--hashtable
prints for each torrent it's hash, index, and name

--addurl [URL] [*DOWNLOAD_DIR (integer)] [*PATH]
adds a torrent job from the given URL

--torrentslist
prints torrents list with their properties

--getsettings
prints utorrent settings

--getfiles [INDEX]
get the list of files in a torrent job

--setsettings [STRING]
set setting or multiple settings.

--getprops [INDEX]
get a list of the various properties for a torrent job

--start [INDEX]
start torrent

--stop [INDEX]
stop torrent

--pause [INDEX]
pause torrent

--forcestart [INDEX]
force torrent start

--unpause [INDEX]
unpause torrent

--recheck [INDEX]
recheck the torrent contents for the specified torrent

--remove [INDEX]
remove the specified torrent from the torrent jobs list

--removedata [INDEX]
remove the torrent from the jobs list and it's content

--removetorrent [INDEX]
remove the torrent from jobs list and the torrent file

--removedatatorrent [INDEX]
remove torrent from the jobs list, it's content and torrent file

--transferhistory
returns the current transfer history

--resettransferhistory
resets the current transfer history

--getversion
returns information about the server

--listdirs
returns list of download directories

--setprio [INDEX] [FILE_INDEX] [PRIORITY]
set priority for specified file(s)

--request [REQUEST]
pass your own request to the server
"""

import urllib2
import re
import json
import sys
import settings



class Torrent:
	""" Class contains methods for working with torrents """

	def __set_opener(self):
		""" returns an opener with url, user, passwd """
		auth_handler = urllib2.HTTPBasicAuthHandler()
		
		auth_handler.add_password(realm='uTorrent',
		uri=settings.WEBUI,
		user=settings.USER, 
		passwd=settings.PASSWD)
		
		opener = urllib2.build_opener(auth_handler)
		return opener
	
	def __token(self):
		""" extract token and cookie """
		
		opener = self.__set_opener()
		urllib2.install_opener(opener)
		token_location = settings.WEBUI + 'token.html'
		
		# open token location
		try:
			response = urllib2.urlopen(token_location)
		except:
			print "[error]: error opening token page.\nCheck your settings at settings.py.\nexiting."
			response.close()
			sys.exit(0)
			
		# get cookie
		cookie = response.headers['Set-Cookie']
		#print "[dbg] Cookie ... " + cookie
		
		hrml_page = response.read()
		response.close()
		
		# extract token
		token = re.compile('>([^<]+)<')
		matches = re.search(token, hrml_page)
		token = matches.group(0)[1:-1]

		# save token & cookie for reuse.
		authreuse = open(settings.AUTH_SAVE_PATH, "w")
		authreuse.write(token + "%" + cookie)
		authreuse.close()
		
		return (token, cookie)
	
	def __request(self, action):
		""" all API goes thru this method """

		opener = self.__set_opener()

		# try to load previous token & cookie
		try:
			authreuse = open(settings.AUTH_SAVE_PATH, "r")
			token, cookie = authreuse.read().split("%")
			#print "[dbg]: reusing:\nToken: {0}\nCookie: {1}\n".format(token, cookie)
		except:
			# token or cookie not reusable, requesting new
			#print "[dbg]: request new token, cookie"
			(token, cookie) = self.__token()
		
		# since every request needs a cookie, put it into header.
		opener.addheaders = [('Cookie', cookie)]
		urllib2.install_opener(opener)
	
		target = settings.WEBUI + "?token=" + token + action
		#print "[dbg] Request ... " + target

		try:
			response = urllib2.urlopen(target)
		except:
			print "[error]: error opening {0}\nCleaning auth data at `{1}`. Try again now.\nexiting.".format(target, settings.AUTH_SAVE_PATH)
			authreuse = open(settings.AUTH_SAVE_PATH, "w")
			authreuse.close()
			sys.exit(0)
																				 
		# we got json
		data = response.read()
		#print "[dbg] Data size: %s\n" % (len(data))
		return data

	def hashtable(self):
		""" prints for each torrent it's hash, index and name """
		torrents = json.loads(self.__request("&list=1"))['torrents']
		index = 0
		print "--------------------------------"
		
		if torrents == []:
			print "No torrent jobs."
			print "--------------------------------"
		else:
			for each in torrents:
				print "index: {0}\nhash: {1}\ntorrent: {2}".format(index, each[0], each[2])
				print "--------------------------------"
				index += 1

	def index2hash(self, index):
		""" get torrent index and return torrent hash """
		#print "[dbg]: input: " + str(index)
		return json.loads(self.__request("&list=1"))['torrents'][index][0]


##### API ######
	def torrents_list(self):
		""" prints all torrent jobs """
		torrents = json.loads(self.__request("&list=1"))['torrents']
		torrent_props = TorrentProperties(torrents)
		torrent_props.print_all()

	def getsettings(self):
		""" prints settings of utorrent """
		print self.__request("&action=getsettings")
		
	def getfiles(self, options):
		""" prints torrent files of specified torrent job """
		torrent_index = int(options[0])
		files_json = json.loads(self.__request("&action=getfiles&hash=" + self.index2hash(torrent_index)))

		files = TorrentFiles(files_json)
		files.print_files()

	def setsettings(self, options):
		""" set utorrent settings. i.e max_ul_rate=10 """
		settings = re.sub('\s+', '', options[0])

		req = '&action=setsetting'
		splitted = settings.split('&')
		for opts in splitted:
			try:
				(setting, value) = opts.split('=')
			except:
				print "[Error]: Failed to parse `{0}`. exiting.".format(options[0])
				sys.exit(0)

			# build request string
			req += "&s=" + setting + "&v=" + value

		self.__request(req)

	
	def getprops(self, options):
		""" print properties for specified torrent """
		torrent_index = int(options[0])
		props_dict = json.loads(self.__request("&action=getprops&hash=" + self.index2hash(torrent_index)))['props'][0]

		props = TorrentJob(props_dict)
		props.print_props()

	def start(self, options):
		""" start torrent """
		torrent_index = int(options[0])
		print self.__request("&action=start&hash=" + self.index2hash(torrent_index))

	def stop(self, options):
		""" stop torrent """
		torrent_index = int(options[0])
		print self.__request("&action=stop&hash=" + self.index2hash(torrent_index))

	def pause(self, options):
		""" pause torrent """
		torrent_index = int(options[0])
		print self.__request("&action=pause&hash=" + self.index2hash(torrent_index))

	def forcestart(self, options):
		""" force start torrent """
		torrent_index = int(options[0])
		print self.__request("&action=forcestart&hash=" + self.index2hash(torrent_index))

	def unpause(self, options):
		""" unpause torrent """
		torrent_index = int(options[0])
		print self.__request("&action=unpause&hash=" + self.index2hash(torrent_index))

	def recheck(self, options):
		""" recheck torrent contents """
		torrent_index = int(options[0])
		print self.__request("&action=recheck&hash=" + self.index2hash(torrent_index))

	def remove(self, options):
		""" remove the specified torrent from the torrent jobs list """
		torrent_index = int(options[0])
		print self.__request("&action=remove&hash=" + self.index2hash(torrent_index))

	def removedata(self, options):
		""" remove the torrent from the jobs list and it's content """
		torrent_index = int(options[0])
		print self.__request("&action=removedata&hash=" + self.index2hash(torrent_index))

	def removetorrent(self, options):
		""" remove the torrent from jobs list and the torrent file """
		torrent_index = int(options[0])
		print self.__request("&action=removetorrent&hash=" + self.index2hash(torrent_index))

	def removedatatorrent(self, options):
		""" remove torrent from the jobs list, it's content and torrent file """
		torrent_index = int(options[0])
		print self.__request("&action=removedatatorrent&hash=" + self.index2hash(torrent_index))

	def setprio(self, options):
		""" set priority for specified file(s) """

		torrent_index = int(options[0])
		file_index = int(options[1])
		priority = int(options[2])
		
		
		print self.__request("&action=setprio&hash=" + self.index2hash(torrent_index)
					   + "&p=" + str(priority) + "&f=" + str(file_index))

	def getxferhist(self):
		""" prints the current transfer history """
		print self.__request("&action=getxferhist")

	def resetxferhist(self):
		""" resets the current transfer history """
		print self.__request("&action=resetxferhist")

	def getversion(self):
		""" prints information about the server """
		print self.__request("&action=getversion")

	def addurl(self, options):
		""" adds a torrent from the given URL """

		torrent_url = options[0] # first parameter is url

		try:
			download_dir = int(options[1]) # second (optional) is the download dir (int)
		except:
			download_dir = 0

		try:
			path = options[2] # thid optional is the path (str)
		except:
			path = ''
	
		addurl_req = "&action=add-url&s=" + torrent_url
		
		# handle optional parameters
		if download_dir > 0:
			addurl_req += "&download_dir=" + str(download_dir)
		if path != '':
			addurl_req += "&path=" + path
			
		print self.__request(addurl_req)

	def addfile(self):
		""" add file from hd. !!NOT IMPLEMENTED!!. """
		print "Sorry, not implemented. See README for workaround."

	def listdirs(self):
		""" prints list of download directories """
		
		dir_list = json.loads(self.__request("&action=list-dirs"))["download-dirs"]

		index = 0
		for each in dir_list:
			print "index: {0}".format(index)
			print "path: {:>4}".format(each['path'])
			print "free: {:>4}\n".format(each['available'])
			
			index += 1

##### ENDOF API ######


##### ADDITIONAL #######
			
	def request(self, options):
		"""
		pass your own request.
		look at utorrent server documentation for all available actions.
		"""

		action = "&action=" + options[0]
		print self.__request(action)
				

	def see_help(self):
		""" help """
		print __doc__

##### ENDOF ADDITIONAL #######



# TorrentProperties, TorrentFiles, TorrentJob
# are classes for extracting data.
class TorrentProperties:
	"""
	This class contains all properties for all torrents.

	TODO: some properties contain values in bytes.
		convert them to mb, kb/s and etc.

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
		if self.torrents == []:
			print "No torrent jobs."
		else:
			index = 0
			for each in self.torrents:
				print """
index: {0}
name: {1}
size: {2}
completed: {3}%
status: {4}
""".format(index, 
		each['name'].encode('utf-8'),
		repr_size(each['size']), 
		float(each['percent progress']) / 10.0,
		repr_status(each['status']))
				index += 1
						

		

		
		
class TorrentFiles:
	""" Class contains properties for torrent files """
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

		print "torrent hash: " + self.thash
		file_index = 0
		for each in self.files:
			print """
index: {0}
file: {1}
size: {2}
downloaded: {3}
priority: {4}
""".format(file_index, each['filename'], 
		repr_size(each['filesize']), 
		each['downloaded'], 
		each['priority'])
			file_index += 1



class TorrentJob:
	""" Class contains properties for torrent job """

	def __init__(self, props_dict):
		self.props = {}
		self.props = props_dict

	def print_props(self):
		""" print torrent job properties """
		# adjust output for your needs
		print self.props['hash']
		print self.props['trackers']
	

class Executer:
	""" Class for dealing with console arguments """
	
	@staticmethod
	def run(console_input):
			
		command = ''
		options = []

		# preffered command name -> method name (of Torrent class)
		aliases = {
			'torrentslist': 'torrents_list',
			'getsettings': 'getsettings',
			'getfiles': 'getfiles',
			'setsettings': 'setsettings',
			'getprops': 'getprops',
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
			'hashtable': 'hashtable',
			'help': 'see_help'
		}

		#print "[dbg]: console_input: " + str(console_input)

		try:	
			command = console_input[0]
		except:
			print "[error]: no command was supplied. exiting."
			sys.exit(0)

		try:	
			options = console_input[1:]
		except:
			options = []

		
		command = re.sub(r'-+', '', command) # remove --, -
		
		torrent = Torrent()
		#print "[dbg]: executing: {0}".format(self.alias_of(command))
		
		if aliases.has_key(command):
			call_method = getattr(torrent, aliases[command])
		else:
			print "No such command. read --help."
			sys.exit(0)

		if len(options) > 0:
			call_method(options) # if options supplied, pass them.
		else:
			#try:
			call_method() # otherwise, call method without any options
			#except TypeError:
				#print "[error]: error calling method `{0}` with following options: `{1}`".format(call_method.__name__, options)


###### REPRESENT FUNCTIONS
# repr_ functions used for representing size, status etc in
# human readable form.
# used by classes: TorrentFiles, TorrentProperties
def repr_status(status):
	""" returns a string that represents torrent's current statuses """
		
	status_string = '| '
		
	all_statuses = ( (1, "Started"),
		(2, "Checking"),
		(4, "Start after check"),
		(8, "Checked"),
		(16, "Error"),
		(32, "Paused"),
		(64, "Queued"),
		(128, "Loaded")
		)
				
	for each in all_statuses:
		if status & each[0]:
			status_string += each[1] + ' | '

	return status_string
		
		
# this one taken from 
# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# convert bytes to kb, mb and etc.
def repr_size(size_bytes):
	"""
	format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
	Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
	e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
	"""
	if size_bytes == 1:
		return "1 byte"

	suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]

	bytes_float = float(size_bytes)
	for suffix, precision in suffixes_table:
		if bytes_float < 1024.0:
			break
				
		bytes_float /= 1024.0

	if precision == 0:
		formatted_size = "{0}".format(bytes_float)
	else:
		formatted_size = str(round(bytes_float, ndigits=precision))

	return "{0} {1}".format(formatted_size, suffix)
		

		
# main
args = sys.argv[1:]
Executer.run(args)
