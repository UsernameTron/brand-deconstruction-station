# 🎭 Brand Deconstruction Station - Easy Start Guide

Welcome! This guide is designed to help you get the **Brand Deconstruction Station** running on your computer quickly and easily.

## 🚀 How to Run the App

We use a tool called **Docker** to make running this application super simple. It's like a container that holds everything the app needs to run, so you don't have to install a bunch of complicated software.

### Prerequisites

1.  **Install Docker Desktop**:
    *   Download and install Docker Desktop for your computer (Windows or Mac) from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).
    *   Open Docker Desktop and make sure it's running.

### Running the App

1.  **Open your Terminal (Mac) or Command Prompt (Windows)**.
2.  **Copy and paste** the following command and press **Enter**:

    ```bash
    docker run -p 3000:3000 usernametron/usernametrondeconstruction.station:latest
    ```

    *(Note: This might take a minute the first time as it downloads the necessary files.)*

3.  **That's it!** Once you see messages appearing in the terminal, the app is running.

### Accessing the App

Open your web browser (like Chrome or Safari) and go to:

👉 **[http://localhost:3000](http://localhost:3000)**

## 🛑 How to Stop the App

To stop the application, simply go back to your Terminal window and press **`Ctrl + C`** on your keyboard.

## ❓ Need Help?

If you run into any issues:
*   Make sure Docker Desktop is running.
*   Check that no other application is using port 3000.
*   Try restarting Docker Desktop.

Enjoy deconstructing brands! 🕵️‍♀️✨
