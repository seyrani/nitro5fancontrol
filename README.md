**NitroSense Fan Control**

This project is a PyQt5-based graphical user interface (GUI) application for controlling the fan speed and power modes on Acer Nitro series laptops running Linux Mint. The application communicates with the hardware's embedded controller via the acpi\_ec kernel module.

**Features**

* **Power Mode Control**: Switch between Quiet, Default, and Performance modes.
* **Fan Mode Control**: Options for Auto, Custom (%0-100), and Max fan speed.
* **Debugging Tools**: Read EC data, check power data, and restart Nvidia power management.
* **User-Friendly Interface**: Intuitive GUI designed with PyQt5.
* **Linux Mint Compatibility**: Tested on Linux Mint 22.1 and similar systems.

**Requirements**

* **Operating System**: Linux Mint 22.1 or other Ubuntu-based distributions
* **Python**: 3.12 or higher
* **PyQt5**: Python library required for the GUI
* **acpi\_ec**: Kernel module for communication with the embedded controller
* **Root Privileges**: Sudo access required to access /dev/ec

**Installation**

1. **Clone the Repository**

   ```bash
   git clone https://github.com/<username>/nitrofan-control.git
   cd nitrofan-control
   ```

2. **Install Required Libraries**
   Run the following commands in the terminal to install PyQt5 and other dependencies:

   ```bash
   sudo apt update
   sudo apt install python3-pyqt5
   ```

3. **Load the acpi\_ec Module**
   Make sure the acpi\_ec module is loaded:

   ```bash
   sudo modprobe acpi_ec
   lsmod | grep acpi_ec
   ```

   Output: `acpi_ec 12288 0` should appear.

   If the module is not loaded, compile and install it from the MusiKid/acpi\_ec repository:

   ```bash
   git clone https://github.com/MusiKid/acpi_ec.git
   cd acpi_ec
   make
   sudo make install
   sudo modprobe acpi_ec
   ```

4. **Set Permissions for /dev/ec**
   Grant read/write permissions to the /dev/ec file:

   ```bash
   sudo chmod 660 /dev/ec
   ls -l /dev/ec
   ```

   Output: `crw-rw---- 1 root root 506, 0` should appear.

   To make the permission change permanent, add a udev rule:

   ```bash
   echo 'KERNEL=="ec", MODE="0660", OWNER="root", GROUP="root"' | sudo tee /etc/udev/rules.d/99-acpi_ec.rules
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

5. **Configure X11 Display Permissions**
   When running the GUI with sudo, configure X11 display access:

   ```bash
   xhost +local:root
   ```

**Usage**

* **Run the Application**:

  ```bash
  sudo python3 main.py
  ```

  If you get an X11 error, use the `xhost` command mentioned above.
  To revoke the X11 permission after running the application:

  ```bash
  xhost -local:root
  ```

**GUI Usage**

* **Power Mode**: Select Quiet, Default, or Performance mode.

* **Fan Mode**: Choose Auto, Custom, or Max mode. In Custom mode, you can adjust the fan speed from 0% to 100%.

* **Apply Settings**: Click the button to save the selected settings.

* **Debugging**:

  * **Read EC**: Read the contents of /dev/ec.
  * **Power Data**: Display system power consumption data.
  * **Restart Nvidia-Powerd**: Restart Nvidia power management.

* **Check Logs**: The text field in the GUI will show logs of operations and errors.

**Troubleshooting**

1. **Error: /dev/ec Not Found**:

   * Ensure the acpi\_ec module is loaded: `lsmod | grep acpi_ec`
   * To load the module: `sudo modprobe acpi_ec`
   * For more information: [MusiKid/acpi\_ec](https://github.com/MusiKid/acpi_ec)

2. **Error: /dev/ec Permissions Insufficient**:

   * Check permissions: `ls -l /dev/ec`
   * Fix permissions: `sudo chmod 660 /dev/ec`
   * Add a udev rule for permanent solution (as mentioned above).

3. **Error: PyQt5 Cannot Be Imported**:

   * Ensure PyQt5 is installed: `python3 -m pip show PyQt5`
   * To install: `sudo apt install python3-pyqt5`

4. **Error: GUI Not Opening (X11 Error)**:

   * Check the X11 environment: `echo $XDG_SESSION_TYPE`
   * If output is `x11`: `xhost +local:root`
   * If output is `wayland`, additional configuration may be needed to run the GUI with sudo on Wayland.

5. **Fan or Power Modes Not Working**:

   * Check the contents of /dev/ec: `sudo xxd -g1 /dev/ec`
   * Verify your device model: `dmidecode -s system-product-name`
   * Review the logs for compatibility with your Acer Nitro device.
