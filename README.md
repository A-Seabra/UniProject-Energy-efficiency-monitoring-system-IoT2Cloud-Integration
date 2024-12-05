# UniProject-Energy_efficiency_monitoring_system_IoT2Cloud_Integration

Energy efficiency monitoring system based in IoT tools and technologies.

Developed by me, Artur Seabra, and my colleague, César Roncon.

The system allows  for the monitoring of the following parameters:

- Interior temperature
- Air conditioning status
- Water temperature limit
- The system controls the air conditioning status and sets the water temperature limits (heated by solar energy) based on the detection of interior temperature, exterior light level, and the movement of windows and doors.

The monitored parameters are sent to a Blynk IO cloud and to the Blynk IO App, which is natively available for Android and iOS.

The data is also sent to another cloud, Adafruit IO, to continuously receive temperature forecasts, 1 hour into the future, using a Python program. 
This program retrieves the latest data from Adafruit IO, makes the forecast using a linear regression model, and sends the forecast back to Adafruit IO.

The Adafruit IO cloud is used because the Blynk IO cloud does not allow free data transfer. Thus, it is specifically used for visualization and executing temperature forecasting.
