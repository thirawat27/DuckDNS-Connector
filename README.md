# DuckDNS Connector

![DuckDNS Connector Icon](logo.ico)

**DuckDNS Connector** is a lightweight, modern, and easy-to-use desktop application for Windows that automatically keeps your DuckDNS domains updated with your public IP address. It runs silently in the system tray, requires minimal setup, and provides notifications to keep you informed.

This application is built with Python and its native `tkinter` library, styled with a modern, dark theme for a clean user interface.

Developed by **thirawat27**.

---

## Features

-   **Automatic Updates:** Runs in the background and checks your IP address at a user-defined interval.
-   **System Tray Integration:** Manages all operations from a convenient icon in your system tray, staying out of your way.
-   **Smart Updates:** Only sends an update request to DuckDNS when your public IP address has actually changed, preventing unnecessary API calls.
-   **Modern UI:** A clean and simple settings panel with a dark theme, built with standard Python libraries.
-   **Notifications:** Optional desktop notifications for successful updates or errors.
-   **Lightweight & Simple:** Just enter your DuckDNS domain and token, and the app handles the rest.

---

## Installation

You can easily install DuckDNS Connector on your Windows machine by following these steps:

1.  **Download the Installer:**
    *   Go to the [**Releases**](https://github.com/thirawat27/DuckDNS-Connector/releases) page of this repository.
    *   Download the latest `DuckDNS-Connector-vX.X.X-Setup.exe` file.

2.  **Run the Installer:**
    *   Double-click the downloaded `.exe` file.
    *   Windows Defender SmartScreen might show a warning because it's a new application. If this happens, click on `More info` and then `Run anyway`.
    *   Follow the on-screen instructions. You can choose to have the application start automatically when you log in to Windows.

3.  **Installation Complete!**
    *   After installation, DuckDNS Connector will start automatically, and you will see its icon in your system tray (near the clock).

---

## How to Use

### First-Time Setup

1.  **Find the Icon:** Locate the DuckDNS Connector icon in your system tray. You may need to click the small upward arrow (^) to see all icons.

2.  **Open Settings:**
    *   **Right-click** on the icon to open the menu.
    *   Select **"Settings"**.

3.  **Configure Your Details:**
    *   **Domain:** Enter your DuckDNS subdomain **only** (e.g., if your domain is `my-home.duckdns.org`, you just need to enter `my-home`).
    *   **Token:** Paste your unique token from the [DuckDNS website](https://www.duckdns.org/).
    *   **Update Interval:** Choose how often the application should check for IP changes (default is 5 minutes).
    *   **Notifications:** Select "YES" or "NO" to enable or disable desktop notifications.

4.  **Save Your Settings:**
    *   Click the **"Save Changes"** button. The application will save your settings and immediately perform an update check.
    *   You will receive a notification confirming that the settings have been saved.

### Daily Operation

Once configured, DuckDNS Connector will run silently in the background. You can right-click the tray icon at any time to:
-   **Force Update:** Immediately check and update your IP address.
-   **Show My Public IP:** Display your current public IP address.
-   **Open Settings:** Change your configuration.
-   **Exit:** Close the application.

---

## Building from Source

If you prefer to build the application from the source code, follow these steps.

### Prerequisites

-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads/) (optional, for cloning)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/thirawat27/DuckDNS-Connector.git
    cd DuckDNS-Connector
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    (Ensure you have a `requirements.txt` file in the project root.)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    python duckdns_connector.py
    ```

5.  **Build the Executable (Optional):**
    To create a standalone `.exe` file, you need PyInstaller. Use the provided `build.spec` file for configuration.
    ```bash
    pip install pyinstaller
    pyinstaller build.spec
    ```
    The final executable will be located in the `dist` folder.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.