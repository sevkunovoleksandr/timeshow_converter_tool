from lib.utils import clean_string, read_file, write_file, zip_file
from lib.process import process
import sys, os, argparse, glob, shlex, time
args = None


def confirm_overwrites(paths):
	if args.yes:
		return True;
	existing = [p for p in paths if os.path.exists(p)]
	if not existing:
		return True
	print("The following files already exist and will be overwritten:")
	for p in existing:
		print("  - " + p)
	r = input("Do you wish to proceed? Yes(y) / No: ").strip().lower()
	return r == "yes" or r == "y"


def resolve_paths(output_folder, output_name, r):
	if output_folder:
		output_folder = os.path.join(output_folder, '')
	p = "" if not args.prefix else args.prefix+"_"
	tn = p + ("tc_" + output_name + ".xml" if output_name else r["tc_file"])
	sn = p + ("seq_" + output_name + ".xml" if output_name else r["seq_file"])
	zn = p + (output_name + ".zip" if output_name else r["zip_file"])
	return {
		"tn": tn, 
		"sn": sn, 
		"zn": zn,
		"tp": output_folder + tn,
		"sp": output_folder + sn,
		"zp": output_folder + zn,
	}


def run(input_path, output_folder="", output_name=None, confirmed=False, processed=None, resolved=None):
	if not os.path.exists(input_path):
		print(f"Invalid input path, no file could be found: {input_path}")
		return 1
	r = processed or process(read_file(input_path))
	t = resolved or resolve_paths(output_folder, output_name, r)
	if args.unpack:
		if confirmed or confirm_overwrites([t["tp"], t["sp"]]):
			write_file(t["tp"], r["timecode"])
			write_file(t["sp"], r["sequence"])
	else:
		if confirmed or confirm_overwrites([t["zp"]]):
			zip_file(t["zp"], {
				t["tn"]: r["timecode"],
				t["sn"]: r["sequence"]
			})
	return 0


def run_batch(input_folder, output_folder):
	file_paths = glob.glob(input_folder+"/*.json")
	overwrites = []
	c = []
	for i, path in enumerate(file_paths):
		s = read_file(path)
		#start = time.perf_counter()
		r = process(s)
		#end = time.perf_counter()
		#print("Perf: " + str(end - start) + " @ " + path)
		t = resolve_paths(output_folder, None, r)
		c.append({ "r":r, "t":t })
		if args.unpack:
			overwrites.append(t["tp"])
			overwrites.append(t["sp"])
		else:
			overwrites.append(t["zp"])
	if confirm_overwrites(overwrites):
		for i, path in enumerate(file_paths):
			ci = c[i]
			run(path, output_folder, None, True, ci["r"], ci["t"])
	return 0;


DESC = "Convert Timeshow JSON into tc_ and seq_ xml files." 
I_TEXT = "Path to the input JSON file."
O_TEXT = "Path to the output folder."
N_TEXT = "Name to use instead of the predefined 'timeshow_name'."
P_TEXT = "Pefix to be attached at the start of the file name."
B_TEXT = "Batch convert the -i (input) folder to the -o (output) folder."
U_TEXT = "Writes the files directly instead of packing them into a zip."
Y_TEXT = "Confirms 'yes' to all overwrites."
HELP_MSG = "Use --help for usage information.\n"

def parse_args(argv=None):
	parser = argparse.ArgumentParser( prog="timeshow_converter", description=DESC )
	parser.add_argument("-i", "--input", help=I_TEXT, required=True)
	parser.add_argument("-o", "--output", help=O_TEXT)
	parser.add_argument("-n", "--name", help=N_TEXT)
	parser.add_argument("-p", "--prefix", help=P_TEXT)
	parser.add_argument("-b", "--batch", help=B_TEXT, action="store_true")
	parser.add_argument("-u", "--unpack", help=U_TEXT, action="store_true")
	parser.add_argument("-y", "--yes", help=Y_TEXT, action="store_true")
	return parser.parse_args(argv)


def main(argv=None):
	global args
	argv = argv or sys.argv[1:]
	if not argv:
		argv = ["--help"]
	args = parse_args(argv)
	if not args.input:
		print("Missing required arguments, an input path must be supplied. " + HELP_MSG)
		return 1
	try:
		if args.batch:
			if not os.path.isdir(args.input):
				print("Input folder not valid.")
				return 1
			if not args.output:
				print("Missing required arguments, 'batch' mode requires an input and output folder to be specified. " + HELP_MSG)
				return 1
			if args.name:
				print("Incompatible arguments, -b 'batch' mode cannot use the -n 'name' argument.")
				return 1
			return run_batch(args.input, args.output)

		if not args.output:
			args.output = "./"
		return run(args.input, args.output, args.name)
	except Exception as e:
		print("An error occured, please check your inputs and try again. " + HELP_MSG + str(e) + "\n")
		return 1


test_args = [
	"-y -i Inputs/120a.json -o Outputs",
	"-y -i Inputs/120a.json -o Outputs -u",
	"-y -i Inputs/120a.json -o Outputs -n name",
	"-y -i Inputs/120a.json -o Outputs -n name -u",
	"-y -i Inputs/120a.json -o Outputs -n name -p prefix",
	"-y -i Inputs/120a.json -o Outputs -n name -p prefix -u",

	"-y -b -i Inputs -o Outputs/Batch",
	"-y -b -i Inputs -o Outputs/Batch -u",
	"-y -b -i Inputs -o Outputs/Batch -p prefix",
	"-y -b -i Inputs -o Outputs/Batch -p prefix -u",
	"-y -b -i Inputs -o Outputs/Batch -p prefix -u -n name",

	#"-i Inputs/120a.json -o Outputs -u",
]
def run_test():
	os.makedirs("Outputs/Batch", exist_ok=True)
	for arg_string in test_args:
		print("py tsc.py " + arg_string)
		main(shlex.split(arg_string))


if __name__ == "__main__":
	a = sys.argv[1:]
	if a and a[0] == "test":
		run_test()
	else:
		sys.exit(main())