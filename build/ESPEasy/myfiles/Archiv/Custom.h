/*
	To modify the stock configuration without changing the EspEasy.ino file :

	1) rename this file to "Custom.h" (It is ignored by Git)
	2) define your own settings below
    3) define USE_CUSTOM_H as a build flags. ie : export PLATFORMIO_BUILD_FLAGS="'-DUSE_CUSTOM_H'"
*/



// make the compiler show a warning to confirm that this file is inlcuded
#warning "**** Using Settings from Custom.h File ***"

/*

#######################################################################################################
Your Own Default Settings
#######################################################################################################

	You can basically ovveride ALL macro defined in ESPEasy.ino.
	Don't forget to first #undef each existing #define that you add below.
	Here are some examples:
*/

#undef BUILD_NOTES
#define BUILD_NOTES " - Openandhome"

#undef	DEFAULT_NAME
#define DEFAULT_NAME		"NAME_AENDERN"			// Enter your device friendly name

#undef	DEFAULT_SSID
#define DEFAULT_SSID		"installnetwork"			   // Enter your network SSID

#undef	DEFAULT_KEY
#define DEFAULT_KEY			"Install@Network"		// Enter your network WPA key

#undef	DEFAULT_AP_KEY
#define DEFAULT_AP_KEY		"configesp"		// Enter network WPA key for AP (config) mode

#undef DEFAULT_IPRANGE_LOW
#define DEFAULT_IPRANGE_LOW  "192.168.0.0"          // Allowed IP range to access webserver
#undef DEFAULT_IPRANGE_HIGH
#define DEFAULT_IPRANGE_HIGH "192.168.255.255"  // Allowed IP range to access webserver
#undef DEFAULT_IP_BLOCK_LEVEL
#define DEFAULT_IP_BLOCK_LEVEL 2                // 0: ALL_ALLOWED  1: LOCAL_SUBNET_ALLOWED  2: ONLY_IP_RANGE_ALLOWED

#undef DEFAULT_DELAY
#define DEFAULT_DELAY       1800                  // Sleep Delay in seconds

#undef DEFAULT_CONTROLLER
#define DEFAULT_CONTROLLER   true              // true or false enabled or disabled, set 1st controller defaults
// using a default template, you also need to set a DEFAULT PROTOCOL to a suitable MQTT protocol !
#undef DEFAULT_PUB
#define DEFAULT_PUB         "sensoren/%sysname%/%tskname%/%valname%" // Enter your pub
//#define DEFAULT_PUB         "schaltsteckdosen/%sysname%/%tskname%/%valname%" // Enter your pub

#undef DEFAULT_SUB
#define DEFAULT_SUB         "sensoren/%sysname%/#" // Enter your sub
//#define DEFAULT_SUB         "schaltsteckdosen/%sysname%/#" // Enter your sub

#undef DEFAULT_SERVER
#define DEFAULT_SERVER      "openhabianpi"       // Enter your Server IP address

#undef DEFAULT_PROTOCOL
#define DEFAULT_PROTOCOL    5                   // Protocol used for controller communications

// Advanced Settings
#undef DEFAULT_USE_RULES
#define DEFAULT_USE_RULES			true	// (true|false) Enable Rules?

#undef DEFAULT_USE_NTP
#define DEFAULT_USE_NTP				true	// (true|false) Use NTP Server

#undef DEFAULT_NTP_HOST
#define DEFAULT_NTP_HOST			"192.168.178.1"		// NTP Server Hostname
#undef DEFAULT_TIME_ZONE
#define DEFAULT_TIME_ZONE			60		// Time Offset (in minutes)
#undef DEFAULT_USE_DST
#define DEFAULT_USE_DST				true	// (true|false) Use Daily Time Saving

#undef BUILD_NOTES
#define BUILD_NOTES                 " - stable"


#ifdef BUILD_GIT
#undef BUILD_GIT
#endif

#define BUILD_GIT "openandhome 0.3"

//MQTT-Retain um nach einem Neustart die Werte zu behalten
#undef DEFAULT_MQTT_RETAIN 
#define DEFAULT_MQTT_RETAIN                     true   // (true|false) Retain MQTT messages?

//Suport für TEMP/Feuchtesensor AM2320(b)
#undef USES_P051
#define USES_P051   // AM2320