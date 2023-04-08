# My Home Assistant configurations

[![GitHub Repo stars][stars-shield]][stars]
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![CI Workflow][ci-workflow-shield]][ci-workflow]
[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

## About

While trying to set up my smart home, I got a lot of inspiration from everyone sharing their Home Assistant configuration. I hope my configuration will also help you to set up your smart home.

If you find anything useful here, please star this repo.

## Project setup

I've set up my configuration with the [packages](https://www.home-assistant.io/docs/configuration/packages/) approach. The reason for this is, that I like to keep related configurations (sensors, automations, scripts, etc) together in a single file, a package.
These [packages](packages) are usually built-in integrations or custom_components.

I've tried to use English naming patterns as much as possible, however, anything that is user-facing is in Dutch. Anything that refers to a place (eg. a room) is also in Dutch.

### UI/Lovelace

My UI setup is also not standard, my [ui-lovelace.yaml](ui-lovelace.yaml) (the main dashboard) contains `include` statements to view files.
All the other dashboards can be found in the [lovelace](lovelace) folder. Here is a specific [config](lovelace/config) for all dashboards.
The dashboards do include [views](lovelace/views) that are separate yaml files, some views include on their turn [cards](lovelace/views/cards). The reason for this split is to reduce the size of yaml files, but also to reuse cards.

### Automations and scripts

Most of my automations and scripts are found in their [package](packages), others that do not really match a package, are in the [automations](automations) folder. This folder is structured on a per room basis.
Some general scripts are in the [scripts](scripts) file.

### Blueprints

I've created a few [blueprints](blueprints/automation/golles/) to repeat logic in different rooms or for different devices.

- [Doow/window climate control](blueprints/automation/golles/door-window-climate-control.yaml)
- [Motion activated scenes](blueprints/automation/golles/motion-activated_scenes.yaml)
- [Aqara magic cube (zigbee2mqtt)](blueprints/automation/golles/zigbee2mqtt_aqara_magic_cube.yaml)
- [Bed light button (Hue smart button, zigbee2mqtt)](blueprints/automation/golles/zigbee2mqtt_hue_smart_button_bed_light_button.yaml)
- [Button press and hold (Hue smart button, zigbee2mqtt)](blueprints/automation/golles/zigbee2mqtt_hue_smart_button_press_and_hold_actions.yaml)
- [Xiaomi switches (zigbee2mqtt)](blueprints/automation/golles/zigbee2mqtt_xiaomi_switch.yaml)

### Custom templates

For the same reason as for blueprints, I've created a few [custom_templates](custom_templates/) to reuse jinja tempaltes.

- [Home Connect helpers](custom_templates/home_connect.jinja)
- [Dutch translation helpers](custom_templates/nl.jinja)
- [Plant sensor helpers](custom_templates/plants.jinja)

If you like any of these blueprints, then you can import these into your own Home Assistant.

### Custom components

Custom components that I've installed are set in the `CUSTOM_COMPONENTS` variable in the [update_resources](scripts/update_resources) script.
There are also a few components that I've developed myself:

| Component                                                               | Installations                                                                                     | Stars                                                                                                 |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [KNMI](https://github.com/golles/ha-knmi)                               | ![](https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/knmi.svg)         | ![starts](https://img.shields.io/github/stars/golles/ha-knmi?style=for-the-badge)                     |
| [Kamstrup 403](https://github.com/golles/ha-kamstrup_403)               | ![](https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/kamstrup_403.svg) | ![starts](https://img.shields.io/github/stars/golles/ha-kamstrup_403?style=for-the-badge)             |
| [Kamstrup MC66C](https://github.com/golles/Home-Assistant-Sensor-MC66C) | ![](https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/mc66c.svg)        | ![starts](https://img.shields.io/github/stars/golles/Home-Assistant-Sensor-MC66C?style=for-the-badge) |

## ESPHome config

My ESPHome configuration is not part of my Home Assistant configuration.
This configuration can be found in my [ESPHome-Config](https://github.com/golles/ESPHome-Config) repository.

[buymecoffee]: https://www.buymeacoffee.com/golles
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/golles/Home-Assistant-Config.svg?style=for-the-badge
[commits]: https://github.com/golles/Home-Assistant-Config/commits/main
[license-shield]: https://img.shields.io/github/license/golles/Home-Assistant-Config.svg?style=for-the-badge
[maintainer]: https://github.com/golles
[maintenance-shield]: https://img.shields.io/badge/maintainer-golles-blue.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/golles/Home-Assistant-Config?style=for-the-badge
[stars]: https://github.com/golles/Home-Assistant-Config/stargazers
[ci-workflow-shield]: https://img.shields.io/github/actions/workflow/status/golles/Home-Assistant-Config/ci.yaml?style=for-the-badge
[ci-workflow]: https://github.com/golles/Home-Assistant-Config/actions/workflows/ci.yaml
