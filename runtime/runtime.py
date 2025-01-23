import os
import redis
import json
import logging
import importlib.util
import time
import zipfile

logger = logging.getLogger("Serverless Runtime")
logger.setLevel(logging.DEBUG)

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', 'input')
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', 'output')
MONITORING_PERIOD = int(os.getenv('REDIS_MONITORING_PERIOD', 5))  # Default: 5 segundos
FUNCTION_ENTRY = os.getenv('FUNCTION_ENTRY', 'handler')  # Default: função 'handler'

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def load_function():
    user_function_path = "/opt/usermodule.py"
    user_zip_path = "/opt/usermodule.zip"

    if os.path.exists(user_zip_path):
        logger.info("Unzipping function files...")
        with zipfile.ZipFile(user_zip_path, 'r') as zip_ref:
            zip_ref.extractall("/opt/function")
        user_function_path = "/opt/function"

    spec = importlib.util.spec_from_file_location("usermodule", user_function_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, FUNCTION_ENTRY)

def monitor_redis_and_execute():
    function = load_function()
    last_data = None

    while True:
        try:
            raw_data = redis_client.get(REDIS_INPUT_KEY)
            if raw_data != last_data:
                last_data = raw_data
                input_data = json.loads(raw_data)
                context = {
                    "env": dict(os.environ),
                }
                logger.info("Executing user function...")
                result = function(input_data, context)
                redis_client.set(REDIS_OUTPUT_KEY, json.dumps(result))
                logger.info("Result saved to Redis.")
        except Exception as e:
            logger.error(f"Error: {e}")
        time.sleep(MONITORING_PERIOD)

if __name__ == "__main__":
    logger.info("Starting Serverless Runtime...")
    monitor_redis_and_execute()
