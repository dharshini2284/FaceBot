const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const axios = require('axios'); 

const app = express();
app.use(cors());
app.use(express.json());

// Define the backend directory
const backendPath = path.resolve('F:/face-rag/backend');
console.log('Backend path:', backendPath);

// Verify Python executable exists
const pythonPath = 'F:/face-rag/backend/.venv/Scripts/python.exe';
if (!fs.existsSync(pythonPath)) {
    console.error('Python executable not found at:', pythonPath);
} else {
    console.log('Python executable found at:', pythonPath);
}

// Common environment for all Python processes
const pythonEnv = {
    ...process.env,
    NSCameraUseContinuityCameraDeviceType: 'NO'
};

// API to trigger face registration
app.post('/api/register', (req, res) => {
    const { name } = req.body;
    if (!name) {
        return res.status(400).json({ error: 'Name is required' });
    }
    console.log('Calling register.py with name:', name);

    const scriptPath = path.resolve(backendPath, 'register.py');
    const child = spawn(pythonPath, [scriptPath, name], { cwd: backendPath, env: pythonEnv });

    let output = '';
    let errorOutput = '';

    child.stdout.on('data', (data) => {
        output += data.toString();
        console.log('[Python STDOUT]', data.toString());
    });

    child.stderr.on('data', (data) => {
        const msg = data.toString();
        errorOutput += msg;
        console.error('[Python STDERR]', msg);
    });

    child.on('error', (err) => {
        console.error('Spawn error:', err);
        return res.status(500).json({ error: 'Registration failed: ' + err.message });
    });

    child.on('close', (code) => {
        if (res.headersSent) return;
        if (code === 0) {
            res.json({ message: `Face registered for ${name}`, output });
        } else {
            res.status(500).json({ error: `Registration failed with code ${code}: ${errorOutput}` });
        }
    });
});

// API to trigger face recognition
app.get('/api/recognize', (req, res) => {
    console.log('Calling recognize.py');

    const scriptPath = path.resolve(backendPath, 'recognize.py');
    const child = spawn(pythonPath, [scriptPath], { cwd: backendPath, env: pythonEnv });

    let output = '';
    let errorOutput = '';

    child.stdout.on('data', (data) => {
        output += data.toString();
        console.log('[Python STDOUT]', data.toString());
    });

    child.stderr.on('data', (data) => {
        const msg = data.toString();
        errorOutput += msg;
        console.error('[Python STDERR]', msg);
    });

    child.on('error', (err) => {
        console.error('Spawn error:', err);
        return res.status(500).json({ error: 'Recognition failed: ' + err.message });
    });

    child.on('close', (code) => {
        if (res.headersSent) return;
        if (code === 0) {
            res.json({ message: 'Recognition started', output });
        } else {
            res.status(500).json({ error: `Recognition failed with code ${code}: ${errorOutput}` });
        }
    });
});

// API to handle queries by calling the Flask server
app.post('/api/ask', async (req, res) => {
    const { query } = req.body;
    if (!query) {
        return res.status(400).json({ error: 'Query parameter is missing' });
    }

    try {
        // Make a POST request to Flask's /api/ask endpoint
        const response = await axios.post('http://localhost:8765/api/ask', { query });

        // Forward the response from Flask back to the client
        res.json({ answer: response.data.answer });
    } catch (error) {
        console.error('Error querying Flask API:', error);
        res.status(500).json({ error: 'Failed to get an answer from the Flask server' });
    }
});

// Start the Express server
const server = app.listen(5001, () => {
    console.log('Server running on http://localhost:5001');
});
