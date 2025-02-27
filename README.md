# Axis 233D IO Controller for Home Assistant

A custom integration for Home Assistant that enables control and monitoring of digital I/O ports on Axis 233D network cameras.

## Features

- 🔌 Supports 4 digital inputs and 4 digital outputs
- 🔄 Auto-discovery of available I/O ports
- 🔒 Secure authentication with both basic and digest auth support
- 📊 Real-time status monitoring
- ⚡ Switch entity for each output port
- 🔍 Sensor entity for each input port

## Installation

1. Copy the `axis233d` folder to your `custom_components` directory
2. Restart Home Assistant
3. Add integration through the Home Assistant UI:
   - Go to Configuration > Integrations
   - Click the "+ ADD INTEGRATION" button
   - Search for "Axis 233D IO Controller"

## Configuration

The following parameters are required:

| Parameter | Description | Default |
|-----------|-------------|---------|
| IP Address | The IP address of your Axis camera | - |
| Username | Your camera login username | root |
| Password | Your camera login password | - |
| HTTP Port | Camera's HTTP port | 80 |

## Requirements

- Home Assistant 2023.x or newer
- Axis 233D network camera with firmware 5.x or newer
- `requests>=2.25.1`


