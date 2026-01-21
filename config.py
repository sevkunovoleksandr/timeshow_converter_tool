# API
API_ACCESS_KEY = "API" # This is the hardcoded key used for 'tsc-AccessKey' authorization.
API_ACCESS_KEY_ENV = "TSC_ACCESS_KEY" # If this enviroment variable exists, its value will be used for the 'tsc-AccessKey' authorization instead.

# If you want the rate limiter to be per user, a user identifier will have to be provided in the header of the request. 
# -example: "tsc-UserID", if this value is declared here, but not present in the header, the request will be allowed.
# The default value of None will use the senders 'remote address' to hit the rate limiter.
API_RATELIMIT_USERID_HEADER_PARAM = "tsc-UserID" # None
API_RATELIMIT_LOCUST_TESTUSER_IP = {"127.0.0.1"}  # Add any IPs you may want the rate limiter to treat as Locust TestUsers.
API_RATELIMIT = "10/minute" # Max allowed requests per minute from a particular user-id/remote-address.

API_SIZELIMIT = 1024 * 1024 # Max request body size limit, in bytes: (1024 x 1024 == 1MB)
API_DEFAULT_CHUNK_SIZE = 16 * 1024 # Zip stream response chunk size, in bytes: (1024 == 1KB)

API_ZIP_URL = "/convert_zip" # Expects the './Inputs' examples type JSON object | Outputs a stream of a zip file containing the XML's.
API_JSON_URL = "/convert_json" # Expects the './Inputs' examples type JSON object | Outputs a JSON object containing the XML's.
API_ERROR_CODE = 500 # Errors are returned as a JSON object with a response code of 500 and an 'error' parameter containing the reason.


# Network
NET_HOST = "0.0.0.0"
NET_PORT = 8081
NET_HOT_RELOAD = False
NET_SSL_KEY = None #"path/to/key.pem"
NET_SSL_CRT = None #"path/to/cert.pem"


import uvicorn, os
def run_server(name:str):
	uvicorn.run(name, host=NET_HOST, port=NET_PORT, reload=NET_HOT_RELOAD, ssl_keyfile=NET_SSL_KEY, ssl_certfile=NET_SSL_CRT)


def get_access_key():
	return os.getenv(API_ACCESS_KEY_ENV, API_ACCESS_KEY);