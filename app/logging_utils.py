# app/logging_utils.py
import logging
import json
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Add extra fields if they exist (passed via extra={...})
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "status"):
            log_record["status"] = record.status
        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms
            
        # Specific webhook fields [cite: 165]
        if hasattr(record, "message_id"):
            log_record["message_id"] = record.message_id
        if hasattr(record, "dup"):
            log_record["dup"] = record.dup
        if hasattr(record, "result"):
            log_record["result"] = record.result

        return json.dumps(log_record)

def setup_logger():
    logger = logging.getLogger("lyftr_logger")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logger()