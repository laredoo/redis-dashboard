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
    total_bytes_sent = info['net_io_counters_eth0-bytes_sent']
    total_bytes_recv = info['net_io_counters_eth0-bytes_recv']
    total_traffic = total_bytes_sent + total_bytes_recv

    return {
        "percent-network-egress": (
            (total_bytes_sent / total_traffic) * 100 if total_traffic > 0 else 0
        )
    }

def calculate_memory_info(info: Dict[str, Any]) -> Dict[str, Any]:
    cached_memory = info['virtual_memory-cached']
    buffer_memory = info['virtual_memory-buffers']
    total_memory = info['virtual_memory-total']

    return {
        "percent-memory-caching": (
            ((cached_memory + buffer_memory) / total_memory) * 100
        )
    }

def calculate_cpu_moving_average(
    info: Dict[str, Any], 
    env: Dict[str, Any]
) -> Dict[str, Any]:
    cpu_keys = [key for key in info.keys() if key.startswith("cpu_percent-")]
    cpu_keys = cpu_keys[:3]
    moving_averages = {}
    
    for cpu_key in cpu_keys:
        cpu_id = cpu_key.split("-")[-1]
        current_usage = info[cpu_key]
        
        if "cpu_moving_avg" not in env:
            env["cpu_moving_avg"] = {}
        if cpu_id not in env["cpu_moving_avg"]:
            env["cpu_moving_avg"][cpu_id] = []

        cpu_usage_list = env["cpu_moving_avg"][cpu_id]
        cpu_usage_list.append(current_usage)
        if len(cpu_usage_list) > 60:
            cpu_usage_list.pop(0)

        moving_avg = sum(cpu_usage_list) / len(cpu_usage_list)
        moving_averages[f"avg-util-cpu{cpu_id}-60sec"] = moving_avg

    return moving_averages

def handler(input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        env = context.env

        memory_info = calculate_memory_info(input)
        network_info = calculate_network_info(input)
        cpu_moving_avg = calculate_cpu_moving_average(input, env)

        metrics = {
            "timestamp": input["timestamp"],
            **memory_info,
            **network_info,
            **cpu_moving_avg,
        }

        conn.set(REDIS_OUTPUT_KEY, json.dumps(metrics))

        return metrics
    except Exception as e:
        logger.error(f"Error processing metrics: {e}")
        raise
