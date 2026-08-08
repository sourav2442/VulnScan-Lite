import redis

try:
    connection = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )

    connection.set("vulnscan_test", "VulnScan Lite")

    value = connection.get("vulnscan_test")

    print("Redis connection successful!")
    print("Stored value:", value)

except Exception as e:
    print("Redis connection failed!")
    print("Error:", e)