import logging

import uvicorn

from smartplugservice.infrastructure.SmartPlugsRestAPI import SmartPlugsRestAPI

logger = logging.getLogger(__name__)

api = SmartPlugsRestAPI()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    uvicorn.run(api.app, host="0.0.0.0", port=8000, log_config=None)