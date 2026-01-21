from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response
from lib.process import process
from lib.logger import log_info_colored, Fore
from contextlib import asynccontextmanager
import os, io, threading, httpx, asyncio, glob, sys, config, traceback, threading
import logging
import traceback
from lib.utils import zip_contents, write_file
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
	await api_startup()
	yield

app = FastAPI(lifespan=lifespan)


def json_error(msg, errc=500):
	return JSONResponse(
        status_code= errc or config.API_ERROR_CODE, #500
        content={"error": msg}
    )


def get_remote_address_locustuser(request: Request):
	ip = get_remote_address(request)
	if ip in config.API_RATELIMIT_LOCUST_TESTUSER_IP:
		locust_user_id = request.headers.get("locust-user-id")
		if locust_user_id is not None:
			return str(locust_user_id)
	rl_uid_param = config.API_RATELIMIT_USERID_HEADER_PARAM
	if rl_uid_param != None:
		rl_uid = request.headers.get(rl_uid_param)
		if rl_uid:
			return str(rl_uid);
		else:
			return None
	return ip
	

limiter = Limiter(key_func=get_remote_address_locustuser, default_limits=[config.API_RATELIMIT])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return json_error("Rate limit exceeded") # 429


@app.middleware("http")
async def api_auth(request: Request, call_next):
	#if request.url.path == "/convert_json": # protect all urls now
	password = request.headers.get("tsc-AccessKey")
	if password != config.get_access_key():
		return json_error("Unauthorized") # 403
	if "content-length" not in request.headers:
		return json_error("Header parameter 'content-length' is required")
	if int(request.headers["content-length"]) > config.API_SIZELIMIT:
		return json_error("Request too large, " + config.API_SIZELIMIT)
	return await call_next(request)


# @limiter.limit("6/minute") # handled in SlowAPIMiddleware now
@app.post(config.API_JSON_URL, name="cvj")
async def convert_json(request: Request):
	try:
		body = await request.body()
		result = process(body.decode("utf-8"))
		return JSONResponse(content={
			"timecode": result["timecode"],
			"sequence": result["sequence"]
		})
	except Exception as e:
		return json_error("Failed to parse.")


async def stream_buffer(buf: io.BytesIO, chunk_size: int = config.API_DEFAULT_CHUNK_SIZE):
	buf.seek(0)
	for chunk in iter(lambda: buf.read(chunk_size), b""):
		yield chunk


@app.post(config.API_ZIP_URL, name="cvz")
async def convert_zip(request: Request):
    try:
        body = await request.body()
        r = process(body.decode("utf-8"))
        buffer = zip_contents({
            r["tc_file"]: r["timecode"].encode("utf-8"),
            r["seq_file"]: r["sequence"].encode("utf-8")
        })
        return StreamingResponse(
            stream_buffer(buffer),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{r["zip_file"]}"'}
        )
    except Exception as e:
        import logging, traceback
        logging.error("convert_zip error: %s", e)
        logging.error(traceback.format_exc())
        return json_error("Failed to parse.", 500)


if __name__ == "__main__":
	config.run_server("tsc_api:app")


def get_endpoint_for(n):
	ep = app.url_path_for(n)
	return ep if not app.root_path else app.root_path + ep
def get_json_endpoint():
	return get_endpoint_for("cvj")
def get_file_endpoint():
	return get_endpoint_for("cvz")


async def api_startup():
	a = sys.argv[1:]
	if a and a[0] == "test":
		threading.Thread(target=lambda: asyncio.run(test_convert()), daemon=True).start()
	log_info_colored(Fore.MAGENTA, f"Converter API is awaiting JSON requests at endpoint '{get_file_endpoint()}'.");
	log_info_colored(Fore.MAGENTA, "Success response, stream of a 'media_type' zip file with an attached 'filename' in the header.");
	log_info_colored(Fore.MAGENTA, "Failure response, containing an error message, JSON { error:string }");
	log_info_colored(Fore.MAGENTA, "The API requires a 'tsc-AccessKey' header in the request.");
	log_info_colored(Fore.MAGENTA, "The access key can be changed in the 'config.py' file via the 'API_ACCESS_KEY' parameter.");


def get_filename(path):
	return os.path.splitext(os.path.basename(path))[0]


async def test_convert():
	await asyncio.sleep(0.1)
	log_info_colored(Fore.LIGHTYELLOW_EX, "Beginning test API calls...")
	for path in glob.glob("Inputs/*.json"):
		write_output(path, (await test_api_call(path, get_json_endpoint())).json())
		write_file( f"Outputs/API/{get_filename(path)}.zip", (await test_api_call(path, get_file_endpoint())).content )
	log_info_colored(Fore.LIGHTYELLOW_EX, "Test API calls complete.")
	os._exit(0)


async def test_api_call(input_path, ep) -> Response:
	with open(input_path, "r") as f:
		data = f.read()
	async with httpx.AsyncClient() as client:
		url = "http://localhost:" + str(config.NET_PORT) + ep
		res = await client.post(url, content=data, headers={ "tsc-AccessKey": config.get_access_key(), "tsc-UserID": "1" } )
		return res


def write_output(input_path, result):
	base = get_filename(input_path)
	os.makedirs("Outputs/API", exist_ok=True)
	with open(f"Outputs/API/seq_{base}.xml", "w") as f:
		f.write(result["sequence"])
	with open(f"Outputs/API/tc_{base}.xml", "w") as f:
		f.write(result["timecode"])