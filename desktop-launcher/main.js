const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let flaskProcess;

// Check if Flask server is running
function checkServerRunning() {
    return new Promise((resolve) => {
        const http = require('http');
        const req = http.request({ host: 'localhost', port: 3000, timeout: 1000 }, () => {
            resolve(true);
        });
        req.on('error', () => resolve(false));
        req.on('timeout', () => resolve(false));
        req.end();
    });
}

// Start Flask backend
function startFlaskServer() {
    return new Promise((resolve, reject) => {
        const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
        const appPath = path.join(__dirname, '..', 'app.py');
        
        flaskProcess = spawn(pythonPath, [appPath], {
            cwd: path.join(__dirname, '..'),
            stdio: ['ignore', 'pipe', 'pipe']
        });

        flaskProcess.stdout.on('data', (data) => {
            console.log(`Flask: ${data}`);
            if (data.toString().includes('Running on')) {
                resolve();
            }
        });

        flaskProcess.stderr.on('data', (data) => {
            console.error(`Flask Error: ${data}`);
        });

        flaskProcess.on('error', (error) => {
            console.error('Failed to start Flask server:', error);
            reject(error);
        });

        // Timeout after 10 seconds
        setTimeout(() => {
            if (flaskProcess && !flaskProcess.killed) {
                resolve(); // Assume it started even if we didn't see the message
            }
        }, 10000);
    });
}

// Create the main application window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            webSecurity: true
        },
        titleBarStyle: 'default',
        show: false
    });

    // Load the Flask application
    mainWindow.loadURL('http://localhost:3000');

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Set custom title
        mainWindow.setTitle('🎭 Brand Deconstruction Station');
    });

    // Open external links in default browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Development tools (remove in production)
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

// App event handlers
app.whenReady().then(async () => {
    console.log('🎭 Brand Deconstruction Station - Desktop Launcher');
    console.log('📡 Starting Flask backend...');

    try {
        // Check if server is already running
        const isRunning = await checkServerRunning();
        
        if (!isRunning) {
            await startFlaskServer();
            // Wait a bit more for server to fully start
            await new Promise(resolve => setTimeout(resolve, 3000));
        } else {
            console.log('📡 Flask server already running');
        }

        console.log('🎮 Creating application window...');
        createWindow();

    } catch (error) {
        console.error('❌ Failed to start application:', error);
        app.quit();
    }
});

app.on('window-all-closed', () => {
    // Kill Flask process when app closes
    if (flaskProcess && !flaskProcess.killed) {
        flaskProcess.kill();
    }
    
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Cleanup on app quit
app.on('before-quit', () => {
    if (flaskProcess && !flaskProcess.killed) {
        flaskProcess.kill();
    }
});
