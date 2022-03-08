![Banner]("https://gitlab.com/air0-tek/smart-hydroponics/raw/e6c9f6ee879568911f74ab30b45d25607013d161/banner.png")

STEM's smart hydroponics project includes a hydroponics chamber that is mostly computer-controlled, anticipating conditions and adjusting them based on sensor input

---

The system consists of a Raspberry Pi or similarly-capable SBC (single board computer) that hosts a web page, controls communications, and integrates every subsystem. The finished device contains a vast array of sensors and relays. Most control will be performed automatically through software. Manual control can be assumed by an operator at any given time, however.

The brain of the system, the SBC, will not directly interface with sensors and relays. Instead, control is accomplished by a proxy computer with software developed through Arduino. Communications between the systems will be directed through USB serial with JSON-style information formatting.

---

## Goals

* Implement web based control and information viewing
* Implement timer-based event scheduling
* Implement smart logic-based control
* Make it look sexy
