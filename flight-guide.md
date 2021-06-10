<center>

# TUKANO-IKARO FIELD TEST #1<br><small>TucanoRobotics © 2020</small><br><small>Medellín, Colombia</small>

</center>

This document collects the whole protocol, requirements and timeline of events that must be accomplished in order to perform and test the overall behavior of a drone launch using Tukano-Ikaro software platform

:::danger
**Disclaimer:** *Only YOU are a responsible for all the consequences resulting of the good or bad desicions made during the preparation and execution of the mission. TucanoRobotics and all its members are not responsible for any expected or unexpected failure or accident that can occur. Software is provided under [MIT License](https://github.com/josezy/ikaro/blob/master/LICENSE)*
:::

![](https://codimd.s3.shivering-isles.com/demo/uploads/upload_64791ab191bd8f30f9cade07797c51eb.jpg)

Contents:
[TOC]

---

# Goal

Give a grade/comment on the following:

* Simplicity of setup
    * Cloud Control Station access
    * Drone telemetry connection
    * Get drone ready (plug battery/propellers)

* Communication performance
    * Latency over cellular network

* Execution of commands

# Before fly
* Software updated
    * [ ] ikaro (web)
    * [ ] tukano (RPi)
* Place defined
    * [ ] Take off and land point
    * [ ] Route estimations w/ safe margin
* [ ] Radio TX calibrated
* Failsafe
    * [ ] Low battery
    * [ ] Geofence breach
    * [ ] Triggered by switch

# Flight day
* Aircraft preparation
    * [ ] 4G dongle w/ charged SIM card
    * [ ] Connect to Cloud Control Station
    * [ ] Put propellers
    * [ ] Battery charged and connected
* Radio TX linked
    * [ ] Review flight modes switch
* Sensors calibrated
    * [ ] Magnetometer
* [ ] Review failsafe settings

# Safety checks
* [ ] Radio transmission active
* [ ] Guided/Stabilize/RTL flight modes on TX switch
* [ ] Failsafe properly configured
* [ ] Propellers in position (CW/CCW) w/ nuts tight
* [ ] Battery charged and tied
* [ ] Lipo saver attached

# Timeline

```mermaid
gantt
  title             Basic flight
  dateFormat        m:s
  axisFormat        %M:%S

  section Routine 
  Takeoff           : 00:00,10s
  Goto point 1      : 20s
  Hover             : 30s
  Goto point 2      : 20s
  Return home       : 20s

```

# Emergency escenarios

Keep an eye on the drone and prepare to take control with the radio TX.

## Telemetry connection lost
* Set throttle to 60% and switch to STABILIZE mode
* Switch to RTH flight mode
* Trigger failsafe

## Radio link lost
* Check Cloud Control Station for connection
    * Trigger RTH
* Change pilot location and point radio to aircraft

## LiPo saver beeping or random/unexpected behavior
* Click pause button on CCS
* Trigger RTH from CCS
* Trigger RTH from TX radio
* Trigger failsafe from TX radio
* Try to land on position

---

Happy flight! :airplane:
