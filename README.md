# 🐍 Python Projects

<div align="center">

### A colorful collection of Python experiments, utilities, and applications

Small, independent projects exploring **automation · desktop apps · networking · media · data · machine learning**

![Python projects](https://img.shields.io/badge/Python-projects-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Topics](https://img.shields.io/badge/Topics-36%20projects-8A2BE2?style=for-the-badge)
![Hands-on](https://img.shields.io/badge/Learn-by%20building-FF8C00?style=for-the-badge)

</div>

Welcome! This repository is a portfolio of standalone Python projects, from short language examples to practical command-line tools, desktop interfaces, and data-science demos. Pick a project below to open its guide, find its requirements, and learn how to run it.

> 🎨 **No single setup fits every project:** dependencies and setup instructions are documented in each project's README. Some projects also need particular operating systems, local assets, external services, or credentials.

## 🧭 Project index

### 🌐 Web, networking & automation

| Project | What it does |
|---|---|
| [Async HTTP](Async%20HTTP/readme.md) | Interactive asynchronous GET, POST, PUT, and DELETE requests to a sample REST API. |
| [Bookmark](Bookmark/readme.md) | Save, search, edit, delete, and open links stored in a local SQLite database. |
| [FixNetwork](FixNetwork/readme.md) | Windows network diagnostics and repair steps, including network-stack and adapter resets. |
| [Internet Speed Test](Internet%20Speed%20Test/readme.md) | Measure download, upload, and ping using Speedtest.net servers. |
| [Port Scanner](Port%20Scanner/readme.md) | Concurrent TCP port scans with IPv4/IPv6, optional banners, and JSON output. |
| [Simple Selenium Scraper](Simple%20Selenium%20Scraper/readme.md) | Use headless Chrome and Selenium to collect cricket-news headlines. |
| [Streamlit Demo](Streamlit/readme.md) | Explore Streamlit widgets, interactive data, and charts in a browser app. |
| [WiFi Radar](Wifi%20Radar/readme.md) | Local Flask dashboard for nearby access points, with live scanning and CSV export. |
| [WiFi Scanner](Wifi%20Scanner/readme.md) | Scan nearby wireless networks and display signal, frequency, and security details. |
| [WiFi Profiles](Wifi%20Profiles/readme.md) | Manage saved Windows Wi-Fi profiles and inspect their stored connection details. |

### 🎧 Media, images & creative tools

| Project | What it does |
|---|---|
| [Image to ASCII](Image%20to%20ASCII/readme.md) | Convert an image into ASCII art saved as a text file. |
| [Image2Cartoon](Image2Cartoon/readme.md) | Apply OpenCV filters to create a cartoon-style image. |
| [Improve MP3 Quality](Improve%20MP3%20Quality/readme.md) | Re-encode MP3 files with configurable bitrate, channels, and sample rate. |
| [Lyrics](Lyrics/readme.md) | Search Genius for song metadata and a lyrics preview. |
| [MP3 Player](MP3%20Player/readme.md) | Shuffle a folder of MP3s with background preloading and crossfade transitions. |
| [MP3 Tags](MP3%20Tags/readme.md) | Read ID3 metadata and technical audio details from an MP3 file. |
| [QR Code](QR%20Code/readme.md) | Generate a styled QR code image from text or a URL. |
| [Remove Background](Remove%20Background/readme.md) | Remove an image background and composite the subject onto a solid backdrop. |
| [Steganography](Stenography/readme.md) | Hide and retrieve text in PNG images using least-significant-bit encoding. |
| [Story Reader](StoryReader/readme.md) | Extract text from a PDF and read it aloud with text-to-speech. |
| [Tag Clouds](TagClouds/readme.md) | Collect web-page text and render a word cloud using an image mask. |
| [Text2Audio](Text2Audio/readme.md) | Desktop text-to-speech app with selectable language and locale options. |

### 🖥️ Desktop apps & system utilities

| Project | What it does |
|---|---|
| [Contact Book](GUI_Apps/README.md) | Desktop contact manager backed by Microsoft SQL Server. |
| [Extract CPU Information](Extract%20CPU%20Information/readme.md) | Display CPU model, architecture, frequency, and core information. |
| [Health Monitor](Health%20Monitor/readme.md) | Live process-memory dashboard with heuristic growth warnings. |
| [Load Libraries](LoadLibraries/readme.md) | Call a compiled C#/.NET calculator library from Python using `pythonnet`. |
| [Password Utility](Password%20Utility/readme.md) | Generate passwords and estimate password strength. |
| [Setup Wizard — Fruit Wiki](SetupWizard/readme.md) | Browse fruit images and descriptions in a paginated desktop GUI. |
| [Simple WhatsApp Sender](Simple%20WhatApp%20Sender/readme.md) | Schedule a WhatsApp message through WhatsApp Web. |
| [Use Twilio](Use%20Twilio/readme.md) | Send SMS or WhatsApp messages and place calls through Twilio. |
| [Use Windows Login](Use%20Windows%20Login/readme.md) | Demonstrate checking the current Windows account credentials. |

### 🧠 Machine learning & data

| Project | What it does |
|---|---|
| [COVID Forecast](ML/COVID%20Forecast/readme.md) | Analyze and forecast daily COVID-19 case data with ARIMA/SARIMAX models. |
| [Salary Prediction](ML/Salary/readme.md) | Train a linear-regression salary model and use it for interactive predictions. |

### 🧩 Python fundamentals & persistence

| Project | What it does |
|---|---|
| [Custom Exception](Custom%20Exception/readme.md) | Define, raise, and catch a custom Python exception. |
| [Database](Database/README.md) | Store and retrieve key-value data using Python's built-in `dbm` module. |
| [Object Clone](Object%20Clone/readme.md) | Demonstrate independent object copies with `copy.deepcopy()`. |

## 🚀 Getting started

1. Choose a project from the index and open its README for the exact requirements and instructions.
2. Install the dependencies listed by that project. A virtual environment is a good way to keep them isolated:

   ```bash
   python -m venv .venv
   ```

   Activate it, then install that project's documented packages.

3. Run the command shown in the project's README, from the directory and with the configuration it specifies.

> 💡 There is no repository-wide `requirements.txt`: installing every project's packages is unnecessary, and some projects rely on operating-system tools or services that cannot be installed with `pip`.

## ⚠️ Before you run a project

- **Network tools:** Only scan systems and networks you own or have permission to assess. `FixNetwork` performs system network resets and is Windows-only; read its guide before running it.
- **Wi-Fi profiles:** The Windows profile utility can display saved network credentials and delete profiles. Use it only on your own machine and review the deletion settings first.
- **File changes:** The MP3 re-encoder replaces original files in place. Back up audio before using it.
- **Credentials and APIs:** Configure your own API tokens, account credentials, connection strings, and phone numbers where a project requires them. Do not commit private credentials.
- **External dependencies:** Some demos need internet access, a browser/driver, FFmpeg, SQL Server, a .NET runtime, or a platform-specific feature; each project guide has details.

## 🗂️ Repository layout

Projects are organized in their own folders, generally with a `Console_Code/` or `GUI_Code/` directory and a project-specific README. The `ML/` folder groups the forecasting and salary-prediction projects; `GUI_Apps/` currently contains the Contact Book application.

---

<div align="center">

✨ **Browse a project, try an idea, and keep learning Python.** ✨

</div>
