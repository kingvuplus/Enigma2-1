from Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate

from Tools.StbHardware import getFPVersion
from enigma import ePicLoad, getDesktop, eSize, eTimer, eLabel, eConsoleAppContainer
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Components.InputDevice import iInputDevices, iRcTypeControl
from Components.AVSwitch import AVSwitch
from os import path
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
import skin

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("About"))
		hddsplit, = skin.parameters.get("AboutHddSplit", (0,))

		AboutText = _("Model: %s %s") % (getMachineBrand(), getMachineName()) + "\n"
		AboutText += _("Image: ") + about.getImageTypeString() + "\n"
		AboutText += _("Kernel version: ") + about.getKernelVersionString() + "\n"                             
                if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: %s") % about.getChipSetString() + "\n"
                AboutText += _("CPU: %s") % about.getCPUString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"
                AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageBuild() + "\n"
		AboutText += _("Coder: Redaouane") + "\n"
		if path.exists('/proc/stb/info/release') and getBoxType() in ('et7000', 'et7500', 'et8500'):
			realdriverdate = open("/proc/stb/info/release", 'r')
			for line in realdriverdate:
				tmp = line.strip()
				AboutText += _("Drivers: %s") % tmp + "\n"
			realdriverdate.close()
		else:
			string = getDriverDate()
			year = string[0:4]
			month = string[4:6]
			day = string[6:8]
			driversdate = '-'.join((year, month, day))
			AboutText += _("Drivers: %s") % driversdate + "\n"
                EnigmaVersion = "Enigma: " + about.getEnigmaVersionString()
		self["EnigmaVersion"] = StaticText(EnigmaVersion)
		AboutText += EnigmaVersion + "\n"
		AboutText += _("Enigma (re)starts: %d\n") % config.misc.startCounter.value

		GStreamerVersion = "GStreamer: " + about.getGStreamerVersionString().replace("GStreamer","")
		self["GStreamerVersion"] = StaticText(GStreamerVersion)
		AboutText += GStreamerVersion + "\n"

		ImageVersion = _("Last upgrade: ") + about.getImageVersionString()
		self["ImageVersion"] = StaticText(ImageVersion)
		AboutText += ImageVersion + "\n"

		AboutText += _("Python version: ") + about.getPythonVersionString() + "\n" + "\n"

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		else:
			fp_version = _("Frontprocessor version: %d") % fp_version
			AboutText += fp_version + "\n"

		self["FPVersion"] = StaticText(fp_version)
		
		skinWidth = getDesktop(0).size().width()
		skinHeight = getDesktop(0).size().height()
		AboutText += _("Skin Name: %s") % config.skin.primary_skin.value[0:-9] + _("  (%s x %s)") % (skinWidth, skinHeight) + "\n"

		if path.exists('/etc/enigma2/EtRcType'):
		        rfp = open('/etc/enigma2/EtRcType', "r")
		        Remote = rfp.read()
			rfp.close
                        AboutText += _("Remote control type") + _(": ") + Remote + "\n"
                else:
                        AboutText += _("Remote control type") + _(": ") + iRcTypeControl.getBoxType() 
                        
                if path.exists('/proc/stb/ir/rc/type'):
		        fp = open('/proc/stb/ir/rc/type', "r")
		        RcID = fp.read()
			fp.close
                        AboutText += _("Remote control ID") + _(": ") + RcID 
		
		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimList(showFBCTuners=False)
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"

		self["HDDHeader"] = StaticText(_("Detected HDD:"))
		AboutText += "\n" + _("Detected HDD:") + "\n"

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			formatstring = hddsplit and "%s:%s, %.1f %sB %s" or "%s\n(%s, %.1f %sB %s)"
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += formatstring % (hdd.model(), hdd.capacity(), hdd.free()/1024.0, "G", _("free"))
				else:
					hddinfo += formatstring % (hdd.model(), hdd.capacity(), hdd.free(), "M", _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		AboutText += hddinfo + "\n\n" + _("Network Info:")
		for x in about.GetIPsFromNetworkInterfaces():
			AboutText += "\n" + x[0] + ": " + x[1]

		self["AboutScrollLabel"] = ScrollLabel(AboutText)
		self["key_green"] = Button(_("Translations"))
		self["key_red"] = Button(_("Latest Commits"))
		self["key_yellow"] = Button(_("Memory Info"))
		self["key_blue"] = Button(_("%s ") % getMachineName() + _("picture"))

		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"red": self.showCommits,
				"green": self.showTranslationInfo,
				"yellow": self.showMemoryInfo,
				"blue": self.showModelPic,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showCommits(self):
		self.session.open(CommitInfo)

	def showMemoryInfo(self):
		self.session.open(MemoryInfo)
		
	def showModelPic(self):
		self.session.open(ModelPic)

class ModelPic(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["ModelPic", "About"]
		
		self["key_green"] = Button(_(" "))
		self["key_red"] = Button(_(" "))
		self["key_yellow"] = Button(_(" "))
		self["key_blue"] = Button(_("%s ") % (getMachineName()) + _("Info"))
		
                self["model"] = Label(_("%s %s") % (getMachineBrand(), getMachineName())) 
		self["boxpic"] = Pixmap()
                self.onFirstExecBegin.append(self.poster_resize)

                self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"blue": self.close
			}, -2)		              
		
        def poster_resize(self):
                if getBoxType() in ('sf108'):
                        model = "sf108.jpg"
                elif getBoxType() in ('sf3038'):
                        model = "sf3038.jpg"
                elif getBoxType() in ('et6x00', 'et6000'):
                        model = "et6x00.jpg"
                elif getBoxType() in ('et6500'):
                        model = "et6500.jpg"
                elif getBoxType() in ('et7000'):
                        model = "et7000.jpg"
                elif getBoxType() in ('et7500'):
                        model = "et7500.jpg"
                elif getBoxType() in ('et8000'):
                        model = "et8000.jpg"
                elif getBoxType() in ('et8500', 'et8500s'):
                        model = "et8500.jpg"
                elif getBoxType() in ('et9000', 'et9x00', 'et9200', 'et9500'):
                        model = "et9x00.jpg"
                elif getBoxType() in ('et10000'):
                        model = "et10000.jpg"
                else:
                        model = None
                        
                poster_path = "/usr/share/enigma2/%s" % model        
                self["boxpic"].hide()
                sc = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                size = self["boxpic"].instance.size()
                self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, "#00000000"))
                if self.picload.startDecode(poster_path, 0, 0, False) == 0:
                        ptr = self.picload.getData()
                        if ptr != None:
                                self["boxpic"].instance.setPixmap(ptr)
                                self["boxpic"].show()                                	
                
class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Translation"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = "(N/A)"

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["key_red"] = Button(_("Cancel"))
		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})

class CommitInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Latest Commits"))
		self.skinName = ["CommitInfo", "About"]
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))

		self["actions"] = ActionMap(["SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"left": self.left,
				"right": self.right
			})

		self["key_red"] = Button(_("Cancel"))

		self.project = 0
		self.projects = [
			("enigma2", "enigma2"),
			("OctagonEightSD", "OctagonEightSD"),
			("OctagonEightFHD", "OctagonEightFHD"),
		]
		self.cachedProjects = {}
		self.Timer = eTimer()
		self.Timer.callback.append(self.readGithubCommitLogs)
		self.Timer.start(50, True)

	def readGithubCommitLogs(self):
		url = 'https://api.github.com/repos/Openeight/%s/commits' % self.projects[self.project][0]
		commitlog = ""
		from datetime import datetime
		from json import loads
		from urllib2 import urlopen
		try:
			commitlog += 80 * '-' + '\n'
			commitlog += url.split('/')[-2] + '\n'
			commitlog += 80 * '-' + '\n'
			for c in loads(urlopen(url, timeout=5).read()):
				creator = c['commit']['author']['name']
				title = c['commit']['message']
				date = datetime.strptime(c['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%x %X')
				commitlog += date + ' ' + creator + '\n' + title + 2 * '\n'
			commitlog = commitlog.encode('utf-8')
			self.cachedProjects[self.projects[self.project][1]] = commitlog
		except:
			commitlog += _("Currently the commit log cannot be retrieved - please try later again")
		self["AboutScrollLabel"].setText(commitlog)

	def updateCommitLogs(self):
		if self.cachedProjects.has_key(self.projects[self.project][1]):
			self["AboutScrollLabel"].setText(self.cachedProjects[self.projects[self.project][1]])
		else:
			self["AboutScrollLabel"].setText(_("Please wait"))
			self.Timer.start(50, True)

	def left(self):
		self.project = self.project == 0 and len(self.projects) - 1 or self.project - 1
		self.updateCommitLogs()

	def right(self):
		self.project = self.project != len(self.projects) - 1 and self.project + 1 or 0
		self.updateCommitLogs()

class MemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.getMemoryInfo,
				"green": self.getMemoryInfo,
				"blue": self.clearMemory,
			})

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Refresh"))
		self["key_blue"] = Label(_("Clear"))

		self['lmemtext'] = Label()
		self['lmemvalue'] = Label()
		self['rmemtext'] = Label()
		self['rmemvalue'] = Label()

		self['pfree'] = Label()
		self['pused'] = Label()
		self["slide"] = ProgressBar()
		self["slide"].setValue(100)

		self["params"] = MemoryInfoSkinParams()

		self['info'] = Label(_("This info is for developers only.\nFor a normal users it is not relevant.\nDon't panic please when you see values being displayed that you think look suspicious!"))

		Typ = _("%s  ") % (getMachineName())
		self.setTitle(Typ + "[" + (_("Memory Info"))+ "]")
		self.onLayoutFinish.append(self.getMemoryInfo)

	def getMemoryInfo(self):
		try:
			ltext = rtext = ""
			lvalue = rvalue = ""
			mem = 1
			free = 0
			rows_in_column = self["params"].rows_in_column
			for i, line in enumerate(open('/proc/meminfo','r')):
				s = line.strip().split(None, 2)
				if len(s) == 3:
					name, size, units = s
				elif len(s) == 2:
					name, size = s
					units = ""
				else:
					continue
				if name.startswith("MemTotal"):
					mem = int(size)
				if name.startswith("MemFree") or name.startswith("Buffers") or name.startswith("Cached"):
					free += int(size)
				if i < rows_in_column:
					ltext += "".join((name,"\n"))
					lvalue += "".join((size," ",units,"\n"))
				else:
					rtext += "".join((name,"\n"))
					rvalue += "".join((size," ",units,"\n"))
			self['lmemtext'].setText(ltext)
			self['lmemvalue'].setText(lvalue)
			self['rmemtext'].setText(rtext)
			self['rmemvalue'].setText(rvalue)
			self["slide"].setValue(int(100.0*(mem-free)/mem+0.25))
			self['pfree'].setText("%.1f %s" % (100.*free/mem,'%'))
			self['pused'].setText("%.1f %s" % (100.*(mem-free)/mem,'%'))
		except Exception, e:
			print "[About] getMemoryInfo FAIL:", e

	def clearMemory(self):
		eConsoleAppContainer().execute("sync")
		open("/proc/sys/vm/drop_caches", "w").write("3")
		self.getMemoryInfo()

class MemoryInfoSkinParams(HTMLComponent, GUIComponent):
	def __init__(self):
		GUIComponent.__init__(self)
		self.rows_in_column = 25

	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "rowsincolumn":
					self.rows_in_column = int(value)
			self.skinAttributes = attribs
		return GUIComponent.applySkin(self, desktop, screen)

	GUI_WIDGET = eLabel
