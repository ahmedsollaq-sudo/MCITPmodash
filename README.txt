MCIT PMO DASHBOARD — OFFLINE EDITION

WINDOWS
1. Extract the ZIP file to a normal folder.
2. Install Python 3 if it is not already installed (select “Add Python to PATH”).
3. Double-click start_dashboard.bat.
4. The dashboard opens automatically in your default browser.
5. Keep the black command window open while using the application.

MACOS / LINUX
1. Extract the ZIP and open Terminal in the extracted folder.
2. Run: chmod +x start_dashboard.sh
3. Run: ./start_dashboard.sh

DOCKER — WINDOWS, MACOS OR LINUX
Prerequisite: Install Docker Desktop (Windows/macOS) or Docker Engine with Docker Compose (Linux).
1. Extract the ZIP file to a normal folder.
2. Open Terminal, PowerShell or Command Prompt in that folder.
3. Build and start the application: docker compose up --build -d
4. Open http://localhost:8765 in your browser.
5. Stop the application: docker compose down
6. Start it again later: docker compose up -d

Windows shortcut: double-click start_docker.bat while Docker Desktop is running.
macOS/Linux shortcut: run chmod +x start_docker.sh once, then run ./start_docker.sh.

Docker reads and writes both data files in the data folder beside compose.yaml.
The data remains available when the container is stopped, removed or rebuilt. Back up the data folder regularly.
Docker mode uses a bind-mount-compatible write method so add, edit and delete operations work with Docker Desktop.

DATA
- All project information is stored in data/MCITProjects.json.
- Add, edit and delete operations immediately update that file.
- The project list shows a concise summary. Click a project to open its full details in a new browser tab.
- Each project also has a History log link. History records are stored in data/ProjectHistoryLog.txt.
- History records can be deleted from the history page after confirmation.
- Each history record has a Reply button. A saved reply is appended to the same record on a new line with its date and time.
- Each history record can be edited. Saving replaces only its log text and keeps the original user and timestamp.
- History records can be searched by log text, user name, or record date.
- History fields use the format: project_code||log_text||user||timestamp.
- Multiline log text is stored safely as \n inside each text-file record and displayed as multiple lines on the history page.
- Back up data/MCITProjects.json and data/ProjectHistoryLog.txt regularly.

STOPPING
Close the command window or press Ctrl+C.

The dashboard works completely offline. No internet connection is required.
