import logging
import sys
from typing import Dict, Any

from fastapi import Response, status
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from apps.src.config import constants
from apps.src.exception.train_exception import TrainException
from apps.src.modules.common.config_manager import ConfigManager
from apps.src.schemas.train_schema import TrainSchema
from apps.src.service.training_service import TrainingService
from apps.src.utils.log.log_message import LogMessage

router = InferringRouter()


@cbv(router)
class TrainingController:
    def __init__(self):
        self.logger = logging.getLogger(constants.LOGGER_INFO_NAME)
        self.log_message = LogMessage()

    @router.post('/train')
    def training_controller(self, train_schema: TrainSchema, response: Response) -> Dict[str, Any]:
        try:
            train_config = ConfigManager.configure(config_type="Training", schema=train_schema)

            training_service = TrainingService(train_config)
            training_service.run_classifier()

            response.status_code = status.HTTP_200_OK
            self.logger.info("Training service execution was successful")

            return {"Message": "Success"}
        except TrainException as te:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.error(self.log_message.make_log_message(
                    line_no=self.log_message.get_line_number(exc_traceback),
                    stack_trace=self.log_message.stack_trace(exc_type, exc_value, exc_traceback)
                )
            )
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return {"Error": str(te)}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.error(self.log_message.make_log_message(
                    line_no=self.log_message.get_line_number(exc_traceback),
                    stack_trace=self.log_message.stack_trace(exc_type, exc_value, exc_traceback)
                )
            )
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return {"Error": "An unexpected error occurred." + str(e)}
