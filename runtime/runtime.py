import os
import time
import redis
import json
import logging
import importlib
import sys
import zipfile
import shutil
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ServerlessRuntime:
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_input_key = os.environ.get('REDIS_INPUT_KEY', 'metrics')
        self.redis_output_key = os.environ.get('REDIS_OUTPUT_KEY', 'metrics_output')
        
        self.monitoring_period = int(os.environ.get('MONITORING_PERIOD', 5))
        
        self.function_path = os.environ.get('FUNCTION_PATH', '/opt/usermodule.py')
        self.function_zip = os.environ.get('FUNCTION_ZIP')
        self.function_handler = os.environ.get('FUNCTION_HANDLER', 'handler')
        
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.redis_client = redis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            decode_responses=True
        )

    def _extract_zip_function(self):
        """
        Extract ZIP file containing function code if provided
        """
        if not self.function_zip:
            return False

        try:
            extract_dir = tempfile.mkdtemp()
            
            if not os.path.exists(self.function_zip):
                self.logger.error(f"ZIP file not found: {self.function_zip}")
                return False
            
            with zipfile.ZipFile(self.function_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            extracted_files = os.listdir(extract_dir)
            self.logger.info(f"Extracted files: {extracted_files}")
            
            sys.path.insert(0, extract_dir)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error extracting ZIP: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _load_function(self):
        """
        Dynamically load the serverless function
        """
        try:
            if self.function_zip:
                if not self._extract_zip_function():
                    raise ValueError("Failed to extract ZIP function")
            
            module_path = self.function_path
            module_dir = os.path.dirname(module_path)
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
            
            module = importlib.import_module(module_name)
            
            handler = getattr(module, self.function_handler)
            
            return handler
        
        except Exception as e:
            self.logger.error(f"Error loading function: {e}")
            raise

    def run(self):
        """
        Main runtime execution method
        """
        try:
            handler = self._load_function()
            
            self.logger.info(f"Serverless runtime started. Monitoring {self.redis_input_key}")
            
            while True:
                try:
                    input_data = self.redis_client.get(self.redis_input_key)
                    
                    if input_data:
                        metrics_dict = json.loads(input_data)
                        
                        context = {}
                        
                        result = handler(metrics_dict, context)
                        
                        self.logger.info("Function executed successfully")
                
                except Exception as e:
                    self.logger.error(f"Error in runtime loop: {e}")
                
                time.sleep(self.monitoring_period)
        
        except Exception as e:
            self.logger.error(f"Critical error in runtime: {e}")

def main():
    runtime = ServerlessRuntime()
    runtime.run()

if __name__ == '__main__':
    main()