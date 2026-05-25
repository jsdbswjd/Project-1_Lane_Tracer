# Main component CMakeLists.
# Add new source files to SRCS as the project grows.

idf_component_register(
    SRCS
        "main.c"
    INCLUDE_DIRS
        "."
    REQUIRES
        # micro-ROS
        micro_ros_espidf_component
        # Networking / Wi-Fi
        esp_wifi
        esp_netif
        esp_event
        nvs_flash
        # OTA
        app_update
        esp_https_ota
        esp_http_client
        # Drivers used by motor / IMU code
        driver
        # FreeRTOS
        freertos
)
