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
        Dynamically load the serverless function from ZIP
        """
        try:
            import os
            import stat

            print(f"Function ZIP path: {self.function_zip}")
            
            if not os.path.exists(self.function_zip):
                print(f"Path does not exist: {self.function_zip}")
                raise ValueError(f"Path does not exist: {self.function_zip}")
            
            file_stat = os.stat(self.function_zip)
            print(f"Path type: {'Directory' if stat.S_ISDIR(file_stat.st_mode) else 'File'}")
            print(f"File permissions: {oct(file_stat.st_mode)}")
            
            if os.path.isdir(self.function_zip):
                zip_files = [f for f in os.listdir(self.function_zip) if f.endswith('.zip')]
                if zip_files:
                    self.function_zip = os.path.join(self.function_zip, zip_files[0])
                    print(f"Found ZIP file in directory: {self.function_zip}")
                else:
                    raise ValueError("No ZIP file found in the directory")
            
            with zipfile.ZipFile(self.function_zip, 'r') as zip_ref:
                extract_dir = tempfile.mkdtemp()
                
                self.logger.info(f"ZIP contents: {zip_ref.namelist()}")
                
                zip_ref.extractall(extract_dir)
            
            extracted_files = os.listdir(extract_dir)
            self.logger.info(f"Extracted files: {extracted_files}")
            
            sys.path.insert(0, extract_dir)
            
            python_files = [f for f in extracted_files if f.endswith('.py')]
            if not python_files:
                raise ValueError("No Python files found in the ZIP")
            
            module_name = os.path.splitext(python_files[0])[0]
            module = importlib.import_module(module_name)
            
            handler = getattr(module, self.function_handler)
            
            return handler
        
        except Exception as e:
            self.logger.error(f"Error loading function from ZIP: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
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