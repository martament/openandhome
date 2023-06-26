/*
  user_config_override.h - user configuration overrides user_config.h for Sonoff-Tasmota

  Copyright (C) 2018  Theo Arends

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef _USER_CONFIG_OVERRIDE_H_
#define _USER_CONFIG_OVERRIDE_H_

// force the compiler to show a warning to confirm that this file is inlcuded
#warning **** user_config_override.h: Using Settings from this File ****
#warning **** Compile with extensions for openandhome ****

/*****************************************************************************************************\
 * USAGE:
 *   To modify the stock configuration without changing the user_config.h file:
 *   (1) copy this file to "user_config_override.h" (It will be ignored by Git)
 *   (2) define your own settings below
 *   (3) for platformio:
 *         define USE_CONFIG_OVERRIDE as a build flags.
 *         ie1 : export PLATFORMIO_BUILD_FLAGS='-DUSE_CONFIG_OVERRIDE'
 *         ie2 : enable in file platformio.ini "build_flags = -Wl,-Tesp8266.flash.1m0.ld -DUSE_CONFIG_OVERRIDE"
 *       for Arduino IDE:
 *         enable define USE_CONFIG_OVERRIDE in user_config.h
 ******************************************************************************************************
 * ATTENTION:
 *   - Changes to SECTION1 PARAMETER defines will only override flash settings if you change define CFG_HOLDER.
 *   - Expect compiler warnings when no ifdef/undef/endif sequence is used.
 *   - You still need to update user_config.h for major define USE_MQTT_TLS.
 *   - All parameters can be persistent changed online using commands via MQTT, WebConsole or Serial.
\*****************************************************************************************************/

/*
Examples :
*/
// -- Master parameter control --------------------
#undef  CFG_HOLDER
#define CFG_HOLDER        0x20230512             // [Reset 1] Change this value to load SECTION1 configuration parameters to flash

// Localisation
#undef MY_LANGUAGE
#define MY_LANGUAGE            de_DE           // German in Germany

// +++ eingestelltes Tasmota-Modul - wenn keines gewaehlt wird, dann ist default SONOFF_BASIC voreingestellt
// +++ SONOFF_S2X / SONOFF_POW / SONOFF_RF / SONOFF_TOUCH / SONOFF_T11 / SONOFF_DUAL_R2 / SONOFF_4CH / SONOFF_4CHPRO
// +++ SHELLY1 / SHELLY2 / BLITZWOLF_BWSHP / MAGICHOME / OBI / WEMOS / TECKIN / TUYA_DIMMER usw.
#undef  MODULE																
#define MODULE      WEMOS // [Module] Select default model from sonoff_template.h


//PROJECT
#undef PROJECT
#define PROJECT                "openandhome"          // PROJECT is used as the default topic delimiter and OTA file name
                                                 //   As an IDE restriction it needs to be the same as the main .ino file

#undef SAVE_DATA
#define SAVE_DATA              10                // [SaveData] Save changed parameters to Flash (0 = disable, 1 - 3600 seconds)
#undef SAVE_STATE
#define SAVE_STATE             1                 // [SetOption0] Save changed power state to Flash (0 = disable, 1 = enable)


// -- Setup your own Wifi settings  ---------------
#undef  STA_SSID1
#define STA_SSID1         "installnetwork"             // [Ssid1] Wifi SSID

#undef  STA_PASS1
#define STA_PASS1         "Install@Network"     // [Password1] Wifi password

#undef  STA_SSID2
#define STA_SSID2         ""             // [Ssid1] Wifi SSID

#undef  STA_PASS2
#define STA_PASS2         ""     // [Password1] Wifi password
#undef WIFI_CONFIG_TOOL
#define WIFI_CONFIG_TOOL  WIFI_MANAGER    // [WifiConfig] Default tool if wifi fails to connect
                                         //   (WIFI_RESTART, WIFI_SMARTCONFIG, WIFI_MANAGER, WIFI_WPSCONFIG, WIFI_RETRY, WIFI_WAIT)
#undef WIFI_IP_ADDRESS
#define WIFI_IP_ADDRESS        "0.0.0.0"         // [IpAddress1] Set to 0.0.0.0 for using DHCP or enter a static IP address

// -- Ota -----------------------------------------
#undef OTA_URL
#define OTA_URL                "https://github.com/martament/openandhome/blob/master/build/Tasmota/releases/tasmota-openandhome-4M.bin"  // [OtaUrl]

// -- Setup your own MQTT settings  ---------------
// Disable MQTT per default
#undef  MQTT_USE                            // +++ mit '0' ist MQTT beim Start deaktiviert
#define MQTT_USE          0                 // [SetOption3] Select default MQTT use (0 = Off, 1 = On)
#undef  MQTT_HOST
#define MQTT_HOST         "openandhome-server" // [MqttHost]

#undef  MQTT_PORT
#define MQTT_PORT         1883                   // [MqttPort] MQTT port (10123 on CloudMQTT)

#undef  MQTT_USER
#define MQTT_USER         "openhabian"         // [MqttUser] Optional user

#undef  MQTT_PASS
#define MQTT_PASS         "xxxx"         // [MqttPassword] Optional password

#undef MQTT_BUTTON_RETAIN
#define MQTT_BUTTON_RETAIN     0                 // [ButtonRetain] Button may send retain flag (0 = off, 1 = on)
#undef MQTT_POWER_RETAIN
#define MQTT_POWER_RETAIN      1                // [PowerRetain] Power status message may send retain flag (0 = off, 1 = on)
#undef MQTT_SWITCH_RETAIN
#define MQTT_SWITCH_RETAIN     0                // [SwitchRetain] Switch may send retain flag (0 = off, 1 = on)
#undef MQTT_SENSOR_RETAIN
#define MQTT_SENSOR_RETAIN     0                // [SwitchRetain] Switch may send retain flag (0 = off, 1 = on)

#undef MQTT_FULLTOPIC
#define MQTT_FULLTOPIC         "%prefix%/%topic%/Sonoff_%06X/" // [FullTopic] Subscribe and Publish full topic name - Legacy topic

// %prefix% token options
#define SUB_PREFIX             "cmnd"            // [Prefix1] Sonoff devices subscribe to %prefix%/%topic% being SUB_PREFIX/MQTT_TOPIC and SUB_PREFIX/MQTT_GRPTOPIC
#define PUB_PREFIX             "stat"            // [Prefix2] Sonoff devices publish to %prefix%/%topic% being PUB_PREFIX/MQTT_TOPIC
#define PUB_PREFIX2            "tele"            // [Prefix3] Sonoff devices publish telemetry data to %prefix%/%topic% being PUB_PREFIX2/MQTT_TOPIC/UPTIME, POWER and TIME

// -- MQTT - Telemetry ----------------------------
#undef TELE_PERIOD
#define TELE_PERIOD            600               // [TelePeriod] Telemetry (0 = disable, 10 - 3600 seconds)

// %topic% token options (also ButtonTopic and SwitchTopic)
#undef MQTT_TOPIC
#define MQTT_TOPIC             "sensoren"           // [Topic] (unique) MQTT device topic

#undef MQTT_GRPTOPIC
#define MQTT_GRPTOPIC          "wemos"         // [GroupTopic] MQTT Group topic

#undef MQTT_CLIENT_ID
#define MQTT_CLIENT_ID         "Sonoff_%06X"       // [MqttClient] Also fall back topic using Chip Id = last 6 characters of MAC address

// -- Syslog --------------------------------------
#undef SYS_LOG_HOST
#define SYS_LOG_HOST           "openandhome-server1"          // [LogHost] (Linux) syslog host
#undef SYS_LOG_PORT
#define SYS_LOG_PORT           514               // [LogPort] default syslog UDP port
#undef SYS_LOG_LEVEL
#define SYS_LOG_LEVEL          LOG_LEVEL_NONE    // [SysLog] (LOG_LEVEL_NONE, LOG_LEVEL_ERROR, LOG_LEVEL_INFO, LOG_LEVEL_DEBUG, LOG_LEVEL_DEBUG_MORE)
#undef SERIAL_LOG_LEVEL
#define SERIAL_LOG_LEVEL       LOG_LEVEL_INFO    // [SerialLog]
#undef WEB_LOG_LEVEL
#define WEB_LOG_LEVEL          LOG_LEVEL_INFO    // [WebLog]

// -- Time - Up to three NTP servers in your region
#undef NTP_SERVER1
#define NTP_SERVER1            "fritz.box"       // [NtpServer1] Select first NTP server by name or IP address (129.250.35.250)
#undef NTP_SERVER2
#define NTP_SERVER2            "de.pool.ntp.org"    // [NtpServer2] Select second NTP server by name or IP address (5.39.184.5)
#undef NTP_SERVER3
#define NTP_SERVER3            "0.de.pool.ntp.org"  // [NtpServer3] Select third NTP server by name or IP address (93.94.224.67)

// +++ Location -------- Orts-Einstellung ---------
// +++                     'Lülsfeld'
#undef  LATITUDE
#define LATITUDE       49.8667   	      	// [Latitude]  +++ Breitengrad-Angabe fuer die Berechnung von Astro-Zeiten
#undef  LONGITUDE                         	
#define LONGITUDE      10.3333  	      	// [Longitude] +++ Laengengrad-Angabe fuer die Berechnung von Astro-Zeiten

// -- Time - Start Daylight Saving Time and timezone offset from UTC in minutes
#undef TIME_DST
#define TIME_DST               North, Last, Sun, Mar, 2, +120  // Northern Hemisphere, Last sunday in march at 02:00 +120 minutes

// -- Time - Start Standard Time and timezone offset from UTC in minutes
#undef TIME_STD
#define TIME_STD               North, Last, Sun, Oct, 3, +60   // Northern Hemisphere, Last sunday in october 02:00 +60 minutes
// Enable support for rules
#define USE_RULES          
// -- Application ---------------------------------
#undef APP_TIMEZONE
#define APP_TIMEZONE           99                 // [Timezone] +1 hour (Amsterdam) (-12 .. 12 = hours from UTC, 99 = use TIME_DST/TIME_STD)
#undef APP_LEDSTATE
#define APP_LEDSTATE           LED_POWER         // [LedState] Function of led (LED_OFF, LED_POWER, LED_MQTTSUB, LED_POWER_MQTTSUB, LED_MQTTPUB, LED_POWER_MQTTPUB, LED_MQTT, LED_POWER_MQTT)
#undef APP_PULSETIME
#define APP_PULSETIME          0                 // [PulseTime] Time in 0.1 Sec to turn off power for relay 1 (0 = disabled)
#undef APP_POWERON_STATE
#define APP_POWERON_STATE      3                 // [PowerOnState] Power On Relay state (0 = Off, 1 = On, 2 = Toggle Saved state, 3 = Saved state)
#undef APP_BLINKTIME
#define APP_BLINKTIME          10                // [BlinkTime] Time in 0.1 Sec to blink/toggle power for relay 1
#undef APP_BLINKCOUNT
#define APP_BLINKCOUNT         10                // [BlinkCount] Number of blinks (0 = 32000)
#undef APP_SLEEP
#define APP_SLEEP              0                 // [Sleep] Sleep time to lower energy consumption (0 = Off, 1 - 250 mSec)

#undef KEY_HOLD_TIME
#define KEY_HOLD_TIME          40                // [SetOption32] Number of 0.1 seconds to hold Button or external Pushbutton before sending HOLD message
#undef SWITCH_MODE
#define SWITCH_MODE            TOGGLE            // [SwitchMode] TOGGLE, FOLLOW, FOLLOW_INV, PUSHBUTTON, PUSHBUTTON_INV, PUSHBUTTONHOLD, PUSHBUTTONHOLD_INV or PUSHBUTTON_TOGGLE (the wall switch state)

#undef TEMP_CONVERSION
#define TEMP_CONVERSION        0                 // [SetOption8] Return temperature in (0 = Celsius or 1 = Fahrenheit)
#undef TEMP_RESOLUTION
#define TEMP_RESOLUTION        1                 // [TempRes] Maximum number of decimals (0 - 3) showing sensor Temperature
#undef HUMIDITY_RESOLUTION
#define HUMIDITY_RESOLUTION    1                 // [HumRes] Maximum number of decimals (0 - 3) showing sensor Humidity
#undef PRESSURE_RESOLUTION
#define PRESSURE_RESOLUTION    1                 // [PressRes] Maximum number of decimals (0 - 3) showing sensor Pressure
#undef ENERGY_RESOLUTION
#define ENERGY_RESOLUTION      3                 // [EnergyRes] Maximum number of decimals (0 - 5) showing energy usage in kWh


// You might even pass some parameters from the command line ----------------------------
// Ie:  export PLATFORMIO_BUILD_FLAGS='-DUSE_CONFIG_OVERRIDE -DMY_IP="192.168.1.99" -DMY_GW="192.168.1.1" -DMY_DNS="192.168.1.1"'

#ifdef MY_IP
#undef  WIFI_IP_ADDRESS
#define WIFI_IP_ADDRESS   MY_IP                  // Set to 0.0.0.0 for using DHCP or IP address
#endif

#ifdef MY_GW
#undef  WIFI_GATEWAY
#define WIFI_GATEWAY      MY_GW                  // if not using DHCP set Gateway IP address
#endif

#ifdef MY_DNS
#undef  WIFI_DNS
#define WIFI_DNS          MY_DNS                 // If not using DHCP set DNS IP address (might be equal to WIFI_GATEWAY)
#endif





#undef USE_ARDUINO_OTA                        // Disable support for Arduino OTA
#undef USE_WPS                                // Disable support for WPS as initial wifi configuration tool
//#undef USE_SMARTCONFIG                        // Disable support for Wifi SmartConfig as initial wifi configuration tool
#undef USE_DOMOTICZ                           // Disable Domoticz
#undef USE_HOME_ASSISTANT                     // Disable Home Assistant
#undef USE_MQTT_TLS                           // Disable TLS support won't work as the MQTTHost is not set
#undef USE_KNX                                // Disable KNX IP Protocol Support
//#undef USE_WEBSERVER                          // Disable Webserver
#undef USE_EMULATION                          // Disable Wemo or Hue emulation
//#undef USE_CUSTOM                             // Disable Custom features
//#undef USE_DISCOVERY                          // Disable Discovery services for both MQTT and web server
//#undef USE_TIMERS                             // Disable support for up to 16 timers
//#undef USE_TIMERS_WEB                         // Disable support for timer webpage
//#undef USE_SUNRISE                            // Disable support for Sunrise and sunset tools
//#undef USE_RULES                              // Disable support for rules
//#undef USE_COUNTER                            // Disable counters
//#undef USE_DS18x20                            // Disable DS18x20 sensor
//#undef USE_DS18x20_LEGACY                     // Disable DS18x20 sensor
//#undef USE_DS18B20                            // Disable internal DS18B20 sensor
#undef USE_I2C                                // Disable all I2C sensors and devices
#undef USE_SPI                                // Disable all SPI devices
#undef USE_DISPLAY                            // Disable Display support
#undef USE_MHZ19                              // Disable support for MH-Z19 CO2 sensor
#undef USE_SENSEAIR                           // Disable support for SenseAir K30, K70 and S8 CO2 sensor
#undef USE_PMS5003                            // Disable support for PMS5003 and PMS7003 particle concentration sensor
#undef USE_NOVA_SDS                           // Disable support for SDS011 and SDS021 particle concentration sensor
#undef USE_SERIAL_BRIDGE                      // Disable support for software Serial Bridge
#undef USE_SDM120                             // Disable support for Eastron SDM120-Modbus energy meter
#undef USE_SDM630                             // Disable support for Eastron SDM630-Modbus energy meter
#undef USE_MP3_PLAYER                         // Disable DFPlayer Mini MP3 Player RB-DFR-562 commands: play, volume and stop
#undef USE_TUYA_DIMMER                        // Disable support for Tuya Serial Dimmer
#undef USE_ARMTRONIX_DIMMERS                  // Disable support for Armtronix Dimmers (+1k4 code)
#undef USE_PS_16_DZ                           // Disable support for PS-16-DZ Dimmer and Sonoff L1 (+2k code)
#undef USE_AZ7798                             // Disable support for AZ-Instrument 7798 CO2 datalogger
#undef USE_PN532_HSU                          // Disable support for PN532 using HSU (Serial) interface (+1k8 code, 140 bytes mem)
#undef USE_PZEM004T                           // Disable PZEM004T energy sensor
#undef USE_PZEM_AC                            // Disable PZEM014,016 Energy monitor
#undef USE_PZEM_DC                            // Disable PZEM003,017 Energy monitor
#undef USE_MCP39F501                          // Disable MCP39F501 Energy monitor as used in Shelly 2
//#undef USE_DHT                                // Disable support for DHT11, AM2301 (DHT21, DHT22, AM2302, AM2321) and SI7021 Temperature and Humidity sensor
#undef USE_MAX31855                           // Disable MAX31855 K-Type thermocouple sensor using softSPI
#undef USE_IR_REMOTE                          // Disable IR driver
#undef USE_WS2812                             // Disable WS2812 Led string
#undef USE_ARILUX_RF                          // Disable support for Arilux RF remote controller
#undef USE_SR04                               // Disable support for for HC-SR04 ultrasonic devices
#undef USE_TM1638                             // Disable support for TM1638 switches copying Switch1 .. Switch8
#undef USE_HX711                              // Disable support for HX711 load cell
#undef USE_RF_FLASH                           // Disable support for flashing the EFM8BB1 chip on the Sonoff RF Bridge. C2CK must be connected to GPIO4, C2D to GPIO5 on the PCB
#undef USE_TX20_WIND_SENSOR                   // Disable support for La Crosse TX20 anemometer
#undef USE_RC_SWITCH                          // Disable support for RF transceiver using library RcSwitch
#undef USE_RF_SENSOR                          // Disable support for RF sensor receiver (434MHz or 868MHz) (+0k8 code)
#undef USE_SM16716                            // Disable support for SM16716 RGB LED controller (+0k7 code)
#undef USE_HRE                                // Disable support for Badger HR-E Water Meter (+1k4 code)
#undef DEBUG_THEO                             // Disable debug code
#undef USE_DEBUG_DRIVER                       // Disable debug code

// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// +++ OPTIONALE FIRMWARE KONFIGURATION                                                     +++
// +++ KEINE oder EINE auswaehlen                                                           +++
// +++ KEINE: entspricht den Einstellungen in my_user_config.h und den oben vorgenommenen.  +++
// +++ EINE:  die dann enthaltenen Features und Sensoren sind in 'RELEASENOTES.md'          +++
// +++        beschrieben, die Einstellungen von Abschnitt 2 werden dadurch ueberschrieben. +++
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

//#define BE_MINIMAL            // +++ 1. Tasmota sonoff-minimal: Minimal Firmware fuer OTA 
//#define USE_CLASSIC           // +++ 2. Tasmota sonoff-classic: mit WPS, SmartConfig und WifiManager
//#define USE_SENSORS           // +++ 3. Tasmota sonoff-sensors: mit den meisten Sensoren
//#define USE_BASIC             // +++ 5. Tasmota sonoff-basic:   OHNE Sensoren
//#define USE_DISPLAYS          // +++ 6. Tasmota sonoff-display: mit aktivierten Display Treibern

// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// +++ ENDE von Abschnitt 2 (SECTION 2)                                                     +++
// +++ Folgende Zeilen nicht aendern                                                        +++
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// Part für das Auslesen von STromzählern
#ifndef USE_SCRIPT
#define USE_SCRIPT
#endif
#ifndef USE_SML_M
#define USE_SML_M
#endif
#ifdef USE_RULES
#undef USE_RULES
#endif
//Ende Part für Stromzähler

#endif  // _USER_CONFIG_OVERRIDE_H_
