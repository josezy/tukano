[![hackmd-github-sync-badge](https://hackmd.io/VCgfbFCmQSuWggG1sR7q8Q/badge)](https://hackmd.io/VCgfbFCmQSuWggG1sR7q8Q)

<center>

# PRUEBAS DE CAMPO TUKANO-IKARO<br><small>TucanoRobotics © 2021</small><br><small>Guarne, Colombia</small>

</center>

Este documento pretende recopilar los protocolos, requerimientos y línea temporal de eventos que deben ser cumplidos con el objetivo de ejecutar y validar el funcionamiento completo de un drone lanzado usando la plataforma IKARO y el software TUKANO.

:::danger
**Descargo de responsabilidad:** *Solo TÚ eres responsable de todas las consecuencias que resulten de las buenas o malas decisiones que se tomen durante la preparación y la ejecución de la misión. TucanoRobotics y todos sus miembros no son responsables por ninguna falla esperada o inesperada, o accidente que pueda ocurrir. El software se provee bajo la licencia [MIT License](https://github.com/josezy/ikaro/blob/master/LICENSE)*
:::

![](https://codimd.s3.shivering-isles.com/demo/uploads/upload_64791ab191bd8f30f9cade07797c51eb.jpg)

Contenido:
[TOC]

---

# Objetivo

Calificar/comentar los siguientes aspectos:

* Simplicidad del montaje
    * Cloud Control Station access
    * Drone telemetry connection
    * Get drone ready (plug battery/propellers)

* Communication performance
    * Latency over cellular network

* Execution of commands

# Antes de volar
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

# Día de vuelo
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

# Lista de seguridad
* [ ] Radio transmission active
* [ ] Guided/Stabilize/RTL flight modes on TX switch
* [ ] Failsafe properly configured
* [ ] Propellers in position (CW/CCW) w/ nuts tight
* [ ] Battery charged and tied
* [ ] Lipo saver attached

# Línea de tiempo

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

# Casos de emergencia

Keep an eye on the drone and prepare to take control with the radio TX.

## Conexión de telemetría perdida
* Set throttle to 60% and switch to STABILIZE mode
* Switch to RTL flight mode
* Trigger failsafe

## Enlace de radio perdido
* Check Cloud Control Station for connection
    * Trigger RTL
* Change pilot location and point radio to aircraft

## Alarma por baja batería de salvalipo o comportamiento extraño/inesperado
* Click pause button on CCS
* Trigger RTL from CCS
* Trigger RTL from TX radio
* Trigger failsafe from TX radio
* Try to land on position

---

Buenos vuelos! :airplane:
