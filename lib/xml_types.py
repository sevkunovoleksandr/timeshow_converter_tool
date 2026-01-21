import xml.etree.ElementTree as ET
from xml.dom import minidom
from lib.utils import uid

MA_VERSION = "2.3.1.1"

def get_xml_string(root: ET.Element) -> str:
	raw = ET.tostring(root, encoding="utf-8")
	return minidom.parseString(raw).toprettyxml(indent="    ", encoding="UTF-8").decode("utf-8")

def CreateGma3Root(timecode=None, sequences=None):
	root = ET.Element("GMA3", {"DataVersion": MA_VERSION})
	if sequences:
		for seq in sequences:
			root.append(seq)
	elif timecode is not None:
		root.append(timecode)
	return root

# ~~ Timecode ~~
def CreateTimecode(parent, *, name, duration):
	return ET.SubElement(parent, "Timecode", {
		"Name": name,
		"Guid": uid(),
		"Cursor": "0.0",
		"Duration": f"{float(duration):.2f}",
		"LoopCount": "0",
		"TCSlot": "-1",
		"AutoStop": "No",
		"SwitchOff": "Keep Playbacks",
		"TimeDisplayFormat": "Default",
		"FrameReadout": "Seconds"
	})

def CreateTrackGroup(parent):
	return ET.SubElement(parent, "TrackGroup", {"Play": "", "Rec": ""})

def CreateMarkerTrack(parent, *, name="Marker"):
	return ET.SubElement(parent, "MarkerTrack", {"Name": name, "Guid": uid()})

def CreateTrack(parent, *, name, target):
	return ET.SubElement(parent, "Track", {
		"Name": name,
		"Guid": uid(),
		"Target": target,
		"Play": "",
		"Rec": ""
	})

def CreateTimeRange(parent):
	return ET.SubElement(parent, "TimeRange", {
		"Guid": uid(),
		"Duration": "To End",
		"Play": "",
		"Rec": ""
	})

def CreateCmdSubTrack(parent):
	return ET.SubElement(parent, "CmdSubTrack")

def CreateCmdEvent(parent, *, name, time, cue_dest):
	return ET.SubElement(parent, "CmdEvent", {
		"Name": name,
		"Time": f"{float(time):.2f}",
		"CueDestination": cue_dest
	})

def CreateRealtimeCmd(parent, *, obj, val_cue_dest):
	return ET.SubElement(parent, "RealtimeCmd", {
		"Type": "Key",
		"Source": "Original",
		"UserProfile": "1",
		"User": "1",
		"Status": "On",
		"IsRealtime": "0",
		"IsXFade": "0",
		"IgnoreFollow": "0",
		"IgnoreCommand": "0",
		"Assert": "0",
		"IgnoreNetwork": "0",
		"FromTriggerNode": "0",
		"IgnoreExecTime": "0",
		"IssuedByTimecode": "0",
		"FromLocalHardwareFader": "1",
		"IgnoreExecXFade": "0",
		"IsExecXFade": "0",
		"Object": obj,
		"ExecToken": "Goto",
		"ValCueDestination": val_cue_dest
	})

# ~~ Sequence ~~
def CreateSequence(parent, *, stack_label, appearance=""):
	attrs = {
		"Name": stack_label,
		"Guid": uid(),
		"Appearance": appearance,
		"AutoStart": "Yes",
		"AutoStop": "Yes",
		"AutoFix": "No",
		"AutoStomp": "No",
		"SoftLTP": "Yes",
		"XFadeReload": "No",
		"SwapProtect": "No",
		"KillProtect": "No",
		"UseExecutorTime": "Yes",
		"OffwhenOverridden": "Yes",
		"SequMIB": "Enabled",
		"AutoPrePos": "No",
		"WrapAround": "Yes",
		"MasterGoMode": "None",
		"SpeedfromRate": "No",
		"Tracking": "Yes",
		"IncludeLinkLastGo": "Yes",
		"RateScale": "One",
		"SpeedScale": "One",
		"PreferCueAppearance": "No",
		"ExecutorDisplayMode": "Both",
		"Action": "Toggle",
	}
	el = ET.SubElement(parent, "Sequence", attrs)
	return el

def CreateDependencyExport(parent, *, size="1"):
	return ET.SubElement(parent, "DependencyExport", {"Size": size})

def CreateDependency(parent, rel_addr):
	return ET.SubElement(parent, "Dependency", {"RelAddr": rel_addr})

def CreateAppearance(parent, name, rgb):
	return ET.SubElement(parent, "Appearance", {
		"Name": name,
		"Guid": uid(),
		"Color": "1.0000000000,1.0000000000,1.0000000000,1.0000000000",
		"BackR": str(rgb[0]),
		"BackG": str(rgb[1]),
		"BackB": str(rgb[2]),
		"BackAlpha": "255"
	})

def CreateCue(parent, *, name, no=None, release=None, assert_val=None, allow_dupes=None, trig_type=None):
	attrs = {
		"Name": name,
		"No": str(no) if no is not None else None,
		"Release": release,
		"Assert": assert_val,
		"AllowDuplicates": allow_dupes,
		"TrigType": trig_type
	}
	return ET.SubElement(parent, "Cue", {k: v for k, v in attrs.items() if v != None})

def CreatePart(parent, *, name=None, cue_in_fade=None, sync=None, morph=None):
	attrs = {
		"Name": name,
		"Guid": uid(),
		"AlignRangeX": "No",
		"AlignRangeY": "No",
		"AlignRangeZ": "No",
		"PreserveGridPositions": "No",
		"MAgic": "No",
		"Mode": "0",
		"Action": "Pool Default",
		"Sync": sync,
		"Morph": morph,
		"CueInFade": cue_in_fade
	}
	return ET.SubElement(parent, "Part", {k: v for k, v in attrs.items() if v != None})
