from locust import HttpUser, task, between, events
from lib.utils import read_file
import glob, config
from threading import Lock

tests = []
tests_lookup = {}
for path in glob.glob("Inputs/*.json"):
	tests.append([path, read_file(path)])
	tests_lookup[path] = tests[-1]

test_header = { 
	"tsc-AccessKey": config.get_access_key(),
	"Content-Type": "application/json"
}


@events.init_command_line_parser.add_listener
def _(parser):
	#parser.add_argument("--wait_time", type=float, default=10, include_in_web_ui=True, help="Time between tasks")
	parser.add_argument("--min_wait", type=float, default=10.5, include_in_web_ui=True, help="Min time in seconds between tasks")
	parser.add_argument("--max_wait", type=float, default=14.5, include_in_web_ui=True, help="Max time in seconds between tasks")
	parser.add_argument("--test_paths", nargs="+", default=["Inputs\\120a.json"], include_in_web_ui=True, help="Files for the task to test (comma seperated).")
	parser.add_argument("--endpoint", type=str, default=config.API_ZIP_URL, include_in_web_ui=True, help="Endpoint for the task.")


class TestUser(HttpUser):
	wait_time = 1 #between(10, 11)
	user_lock = Lock()
	current_id = 0
	

	def on_start(self):
		with TestUser.user_lock:
			self.id = TestUser.current_id
			TestUser.current_id += 1
		self.header = test_header.copy()
		self.header["locust-user-id"] = str(self.id)

	@task
	def convert(self):
		vmin = self.environment.parsed_options.min_wait
		vmax = self.environment.parsed_options.max_wait
		TestUser.wait_time = between(vmin, vmax)
		custom_paths = self.environment.parsed_options.test_paths
		custom_endpoint = self.environment.parsed_options.endpoint
		for i, p in enumerate(custom_paths):
			v = tests_lookup[p]
			self.client.post(custom_endpoint, data=v[1], headers=self.header) # test_header
		pass