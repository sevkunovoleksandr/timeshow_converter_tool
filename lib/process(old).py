import json
from lib.utils import *
from lib.xml_types import *

def process(s: str) -> dict[str, str]:
	data = json.loads(clean_string(s))
	project = data["project"]

	# ~~ Timecode ~~
	root_tc = CreateGma3Root()
	tc = CreateTimecode(root_tc, name=project["export_lable"], duration=project["length"])
	tg = CreateTrackGroup(tc)
	CreateMarkerTrack(tg)

	for stack in data["stacks"]:
		targRel = "Default.Sequences." + stack["stack_lable"]
		targ = "ShowData.DataPools." + targRel
		track = CreateTrack(tg, name=stack["stack_lable"], target=targ)
		tr = CreateTimeRange(track)
		sub = CreateCmdSubTrack(tr)
		for action in stack["actions"]:
			evt = CreateCmdEvent(sub,
				name=action["actions_type"].capitalize(),
				time=action["time_stamp"],
				cue_dest=action["actions_lable"]
			)
			CreateRealtimeCmd(evt, obj=targ, val_cue_dest=targRel + "." + action["actions_lable"])

	# ~~ Sequences ~~
	root_seq = CreateGma3Root()
	for stack in data["stacks"]:
		col = stack["stack_color"]
		appearance = ""
		rgb = None
		if col:
			rgb = hex_to_rgb(col)
			appearance = "TC_Color_" + col

		seq = CreateSequence(root_seq, stack_label=stack["stack_lable"], appearance=appearance)

		if appearance:
			depExp = CreateDependencyExport(seq)
			dep = CreateDependency(depExp, "ShowData.Appearances." + appearance)
			CreateAppearance(dep, appearance, rgb)

		offCue = CreateCue(seq, name="OffCue", release="Yes", assert_val="Assert", allow_dupes="", trig_type="")
		CreatePart(offCue)
		zeroCue = CreateCue(seq, name="CueZero", no="0")
		CreatePart(zeroCue)

		for i, action in enumerate(stack["actions"], start=1):
			cue = CreateCue(seq, name=action["actions_lable"], no=action["action_id"], allow_dupes="") # no=str(i)
			CreatePart(cue, name=action["actions_lable"], cue_in_fade=action["action_value"], sync = "", morph = "")

	n = data["timeshow_name"]
	return {
		"timecode": get_xml_string(root_tc),
		"sequence": get_xml_string(root_seq),
		"tc_file": f"tc_{n}.xml",
		"seq_file": f"seq_{n}.xml",
		"zip_file": f"{n}.zip"
	}
