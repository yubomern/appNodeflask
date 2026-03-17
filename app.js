const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// AJAX endpoint to get initial data
app.get('/initialData', (req, res) => {
    // In a real app, you would fetch this from a database
    const data = {
        message: "This is the initial data fetched via AJAX."
    };
    res.status(200).json(data);
});

// Socket.IO connection handler for real-time updates
io.on('connection', (socket) => {
    console.log('A user connected via Socket.IO');

    // Simulate real-time updates every 3 seconds
    setInterval(() => {
        socket.emit('liveUpdate', { update: `Live update at ${new Date().toLocaleTimeString()}` });
    }, 3002);

    socket.on('disconnect', () => {
        console.log('A user disconnected');
    });
});

const PORT = process.env.PORT || 3002;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
