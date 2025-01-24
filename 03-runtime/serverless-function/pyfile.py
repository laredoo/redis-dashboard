from typing import Any, Dict
import redis
import json
import os
import logging

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_INPUT_KEY = os.environ['REDIS_INPUT_KEY']
REDIS_OUTPUT_KEY = os.environ['REDIS_OUTPUT_KEY']

logger = logging.getLogger("LOGGER START")
logger.setLevel(logging.DEBUG)

conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def calculate_network_info(info: Dict[str, Any]) -> Dict[str, Any]:
    network_info = {}

    total_bytes_sent = info['net_io_counters_eth0-bytes_sent']
    total_bytes_recv = info['net_io_counters_eth0-bytes_recv']
    total_traffic = total_bytes_sent + total_bytes_recv

    network_info["percent-network-egress"] = (
        (total_bytes_sent / total_traffic) * 100 if total_traffic > 0 else 0
    )

    return network_info

def calculate_memory_info(info: Dict[str, Any]) -> Dict[str, Any]:
    memory_info = {}

    cached_memory = info['virtual_memory-cached']
    buffer_memory = info['virtual_memory-buffers']
    total_memory = info['virtual_memory-total']

    memory_info["percent-memory-caching"] = (
        ((cached_memory + buffer_memory) / total_memory) * 100
    )

    return memory_info

def calculate_metrics(
        context: Dict[str, Any], 
        redis_info: Dict[str, Any]
    ) -> Dict[str, Any]:

    metrics = {}
    timestamp = redis_info["timestamp"]
    metrics['timestamp'] = timestamp

    memory_info = calculate_memory_info(redis_info)
    network_info = calculate_network_info(redis_info)

    metrics = {
        **metrics, 
        **memory_info, 
        **network_info,
    }

    return metrics

def handler(
        input: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
    try:
        if isinstance(input, str):
            metrics_dict = json.loads(input)
        else:
            metrics_dict = input
        metrics = calculate_metrics(context, metrics_dict)
        conn.set(REDIS_OUTPUT_KEY, json.dumps(metrics))
        logger.info("Metrics successfully saved to Redis.")
    except Exception as e:
        logger.error(f"Error saving metrics to Redis: {e}")
