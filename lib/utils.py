import uuid, zipfile, io

def uid() -> str:
	return " ".join(f"{b:02X}" for b in uuid.uuid4().bytes)

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
	hex_str = hex_str.strip().lstrip("#")
	return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

#def strip_accents(s: str) -> str:
#	return "".join(
#		c for c in unicodedata.normalize("NFKD", s)
#		if not unicodedata.combining(c) and ord(c) < 128
#	)

def remove_chars(s: str, chars_to_remove: str) -> str:
	return s.translate(str.maketrans("", "", chars_to_remove))

def clean_string(s: str) -> str:
	return remove_chars(s, "?") # strip_accents(s)


def read_file(path):
	with open(path, "r") as f:
		return f.read()

def write_file(path, content: str | bytes):
	mode = 'wb' if isinstance(content, bytes) else 'w'
	with open(path, mode) as f:
		f.write(content)


def zip_contents(contents) -> io.BytesIO:
	buf = io.BytesIO()
	with zipfile.ZipFile(buf, 'w') as zf: # compression=zipfile.ZIP_DEFLATED
		for k, v in contents.items():
			zf.writestr(k, v)
	return buf

def zip_file(path, contents : dict[str, bytes]):
	write_file(path, zip_contents(contents).getvalue())