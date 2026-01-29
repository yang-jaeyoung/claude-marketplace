import { createConnection } from "net";
import { EventEmitter } from "events";
import { spawn } from "child_process";
import * as path from "path";
export class PythonBridge extends EventEmitter {
    socket = null;
    process = null;
    options;
    actualPort = 0;
    requestId = 0;
    pendingRequests = new Map();
    buffer = "";
    connected = false;
    reconnecting = false;
    shouldReconnect = true;
    restarting = false;
    processExitedUnexpectedly = false;
    constructor(options) {
        super();
        this.options = {
            timeout: 180000, // 3분 타임아웃 (pykrx API가 느릴 수 있음)
            ...options,
        };
    }
    async start() {
        // Start the Python bridge process with port 0 for dynamic allocation
        this.process = spawn("python3", [this.options.bridgeScript, "--port", "0"], {
            stdio: ["pipe", "pipe", "pipe"],
            cwd: path.dirname(this.options.bridgeScript),
        });
        // Wait for the BRIDGE_PORT marker from stdout
        const portPromise = new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error("Timeout waiting for bridge port"));
            }, 10000);
            this.process.stdout?.on("data", (data) => {
                const output = data.toString();
                const match = output.match(/BRIDGE_PORT:(\d+)/);
                if (match) {
                    clearTimeout(timeout);
                    resolve(parseInt(match[1], 10));
                }
            });
            this.process.on("error", (err) => {
                clearTimeout(timeout);
                reject(err);
            });
            this.process.on("exit", (code) => {
                if (code !== 0 && !this.connected) {
                    clearTimeout(timeout);
                    reject(new Error(`Bridge process exited with code ${code}`));
                }
            });
        });
        this.process.stderr?.on("data", (data) => {
            console.error(`[Bridge stderr]: ${data}`);
        });
        this.process.on("exit", (code) => {
            console.log(`Bridge process exited with code ${code}`);
            this.connected = false;
            this.process = null;
            this.processExitedUnexpectedly = true;
            this.emit("disconnected");
            // Auto-restart if unexpected exit
            if (this.shouldReconnect && !this.restarting) {
                this.scheduleRestart();
            }
        });
        // Wait for the port to be assigned
        this.actualPort = await portPromise;
        console.log(`Bridge assigned port: ${this.actualPort}`);
        // Connect to the socket
        await this.connect();
    }
    async connect() {
        return new Promise((resolve, reject) => {
            const maxRetries = 10;
            let retries = 0;
            const tryConnect = () => {
                this.socket = createConnection({ host: '127.0.0.1', port: this.actualPort });
                this.socket.on("connect", () => {
                    this.connected = true;
                    // TCP keepalive 설정으로 유휴 연결 끊김 방지
                    this.socket.setKeepAlive(true, 30000);
                    this.emit("connected");
                    resolve();
                });
                this.socket.on("error", (err) => {
                    if (retries < maxRetries) {
                        retries++;
                        setTimeout(tryConnect, 500);
                    }
                    else {
                        this.emit("error", err);
                        reject(err);
                    }
                });
                this.socket.on("data", (data) => {
                    this.handleData(data);
                });
                this.socket.on("close", () => {
                    this.connected = false;
                    this.emit("disconnected");
                    // Try reconnect if process alive, restart only if dead
                    if (this.shouldReconnect && !this.restarting && !this.reconnecting) {
                        this.scheduleReconnect();
                    }
                });
            };
            tryConnect();
        });
    }
    scheduleReconnect() {
        if (this.reconnecting || !this.shouldReconnect)
            return;
        // If process is dead, need full restart
        if (!this.process || this.processExitedUnexpectedly) {
            console.log(`[Bridge] Process dead, scheduling full restart`);
            this.scheduleRestart();
            return;
        }
        // Process is alive - reconnect to same port
        this.reconnecting = true;
        console.log(`[Bridge] Process alive, reconnecting to same port ${this.actualPort}...`);
        setTimeout(async () => {
            try {
                // Clean up old socket
                if (this.socket) {
                    this.socket.removeAllListeners();
                    this.socket.destroy();
                    this.socket = null;
                }
                await this.connect();
                console.log(`[Bridge] Reconnected successfully to port ${this.actualPort}`);
            }
            catch (err) {
                console.error(`[Bridge] Reconnect failed:`, err);
                // Only restart if process has exited
                if (!this.process || this.processExitedUnexpectedly) {
                    this.scheduleRestart();
                }
            }
            finally {
                this.reconnecting = false;
            }
        }, 500);
    }
    scheduleRestart() {
        if (this.restarting || !this.shouldReconnect)
            return;
        this.restarting = true;
        console.log(`[Bridge] Scheduling full process restart...`);
        setTimeout(async () => {
            try {
                // Clean up old socket if exists
                if (this.socket) {
                    this.socket.destroy();
                    this.socket = null;
                }
                // Reset state
                this.processExitedUnexpectedly = false;
                this.connected = false;
                this.actualPort = 0;
                // Start fresh
                await this.start();
                console.log(`[Bridge] Process restarted successfully on port ${this.actualPort}`);
            }
            catch (err) {
                console.error(`[Bridge] Process restart failed:`, err);
            }
            finally {
                this.restarting = false;
            }
        }, 2000);
    }
    async ensureConnected() {
        if (this.connected)
            return;
        // Wait for reconnect/restart if in progress
        if (this.reconnecting || this.restarting) {
            const maxWait = 15000;
            const startTime = Date.now();
            while ((this.reconnecting || this.restarting) && Date.now() - startTime < maxWait) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            if (this.connected)
                return;
        }
        // Try reconnect if process alive, restart if dead
        if (!this.connected) {
            if (this.process && !this.processExitedUnexpectedly) {
                this.scheduleReconnect();
            }
            else {
                this.scheduleRestart();
            }
            // Wait for connection
            const maxWait = 15000;
            const startTime = Date.now();
            while (!this.connected && Date.now() - startTime < maxWait) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        if (!this.connected) {
            throw new Error("Not connected and reconnection/restart failed");
        }
    }
    async stop() {
        // Prevent auto-reconnect during shutdown
        this.shouldReconnect = false;
        // Send shutdown command
        if (this.connected) {
            try {
                await this.call("shutdown", {});
            }
            catch {
                // Ignore errors during shutdown
            }
        }
        // Close socket
        if (this.socket) {
            this.socket.destroy();
            this.socket = null;
        }
        // Kill process
        if (this.process) {
            this.process.kill();
            this.process = null;
        }
        // Reject all pending requests
        for (const [id, pending] of this.pendingRequests) {
            clearTimeout(pending.timer);
            pending.reject(new Error("Connection closed"));
        }
        this.pendingRequests.clear();
        this.connected = false;
    }
    async call(method, params) {
        // Auto-reconnect if disconnected
        await this.ensureConnected();
        if (!this.socket || !this.connected) {
            throw new Error("Not connected after reconnection attempt");
        }
        const id = `req_${++this.requestId}`;
        const request = {
            jsonrpc: "2.0",
            id,
            method,
            params,
        };
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingRequests.delete(id);
                reject(new Error(`Request timeout: ${method}`));
            }, this.options.timeout);
            this.pendingRequests.set(id, {
                resolve: resolve,
                reject,
                timer,
            });
            this.socket.write(JSON.stringify(request) + "\n");
        });
    }
    isConnected() {
        return this.connected;
    }
    handleData(data) {
        this.buffer += data.toString();
        const lines = this.buffer.split("\n");
        this.buffer = lines.pop() || "";
        for (const line of lines) {
            if (!line.trim())
                continue;
            try {
                const response = JSON.parse(line);
                const pending = this.pendingRequests.get(response.id);
                if (pending) {
                    clearTimeout(pending.timer);
                    this.pendingRequests.delete(response.id);
                    if (response.error) {
                        pending.reject(new Error(`[${response.error.code}] ${response.error.message}`));
                    }
                    else {
                        pending.resolve(response.result);
                    }
                }
            }
            catch (e) {
                this.emit("error", new Error(`Invalid JSON response: ${line}`));
            }
        }
    }
}
