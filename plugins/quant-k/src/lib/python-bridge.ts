import { createConnection, Socket } from "net";
import { EventEmitter } from "events";
import { spawn, ChildProcess } from "child_process";
import * as path from "path";

interface PythonBridgeOptions {
  port: number; // Base port hint, 0 for dynamic allocation
  bridgeScript: string;
  timeout?: number;
}

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id: string;
  method: string;
  params: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: "2.0";
  id: string;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export class PythonBridge extends EventEmitter {
  private socket: Socket | null = null;
  private process: ChildProcess | null = null;
  private options: Required<PythonBridgeOptions>;
  private actualPort: number = 0;
  private requestId = 0;
  private pendingRequests = new Map<
    string,
    {
      resolve: (value: unknown) => void;
      reject: (reason: Error) => void;
      timer: NodeJS.Timeout;
    }
  >();
  private buffer = "";
  private connected = false;
  private reconnecting = false;
  private shouldReconnect = true;
  private restarting = false;
  private processExitedUnexpectedly = false;

  constructor(options: PythonBridgeOptions) {
    super();
    this.options = {
      timeout: 60000,
      ...options,
    };
  }

  async start(): Promise<void> {
    // Start the Python bridge process with port 0 for dynamic allocation
    this.process = spawn("python3", [this.options.bridgeScript, "--port", "0"], {
      stdio: ["pipe", "pipe", "pipe"],
      cwd: path.dirname(this.options.bridgeScript),
    });

    // Wait for the BRIDGE_PORT marker from stdout
    const portPromise = new Promise<number>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error("Timeout waiting for bridge port"));
      }, 10000);

      this.process!.stdout?.on("data", (data) => {
        const output = data.toString();
        const match = output.match(/BRIDGE_PORT:(\d+)/);
        if (match) {
          clearTimeout(timeout);
          resolve(parseInt(match[1], 10));
        }
      });

      this.process!.on("error", (err) => {
        clearTimeout(timeout);
        reject(err);
      });

      this.process!.on("exit", (code) => {
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

  private async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const maxRetries = 10;
      let retries = 0;

      const tryConnect = () => {
        this.socket = createConnection({ host: '127.0.0.1', port: this.actualPort });

        this.socket.on("connect", () => {
          this.connected = true;
          this.emit("connected");
          resolve();
        });

        this.socket.on("error", (err) => {
          if (retries < maxRetries) {
            retries++;
            setTimeout(tryConnect, 500);
          } else {
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
          // With dynamic ports, always trigger full restart on disconnect
          if (this.shouldReconnect && !this.restarting) {
            this.scheduleRestart();
          }
        });
      };

      tryConnect();
    });
  }

  private scheduleReconnect(): void {
    // With dynamic ports, socket-only reconnect won't work because
    // the port changes on each process start. Always do full restart.
    this.scheduleRestart();
  }

  private scheduleRestart(): void {
    if (this.restarting || !this.shouldReconnect) return;

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
      } catch (err) {
        console.error(`[Bridge] Process restart failed:`, err);
      } finally {
        this.restarting = false;
      }
    }, 2000);
  }

  private async ensureConnected(): Promise<void> {
    if (this.connected) return;

    // Wait for restart if in progress
    if (this.restarting) {
      const maxWait = 15000;
      const startTime = Date.now();
      while (this.restarting && Date.now() - startTime < maxWait) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      if (this.connected) return;
    }

    // With dynamic ports, always do full restart when disconnected
    if (!this.connected) {
      this.scheduleRestart();
      // Wait for restart
      const maxWait = 15000;
      const startTime = Date.now();
      while (!this.connected && Date.now() - startTime < maxWait) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }

    if (!this.connected) {
      throw new Error("Not connected and restart failed");
    }
  }

  async stop(): Promise<void> {
    // Prevent auto-reconnect during shutdown
    this.shouldReconnect = false;

    // Send shutdown command
    if (this.connected) {
      try {
        await this.call("shutdown", {});
      } catch {
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

  async call<T>(method: string, params: Record<string, unknown>): Promise<T> {
    // Auto-reconnect if disconnected
    await this.ensureConnected();

    if (!this.socket || !this.connected) {
      throw new Error("Not connected after reconnection attempt");
    }

    const id = `req_${++this.requestId}`;
    const request: JsonRpcRequest = {
      jsonrpc: "2.0",
      id,
      method,
      params,
    };

    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, this.options.timeout);

      this.pendingRequests.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
        timer,
      });

      this.socket!.write(JSON.stringify(request) + "\n");
    });
  }

  isConnected(): boolean {
    return this.connected;
  }

  private handleData(data: Buffer): void {
    this.buffer += data.toString();

    const lines = this.buffer.split("\n");
    this.buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const response: JsonRpcResponse = JSON.parse(line);
        const pending = this.pendingRequests.get(response.id);

        if (pending) {
          clearTimeout(pending.timer);
          this.pendingRequests.delete(response.id);

          if (response.error) {
            pending.reject(
              new Error(`[${response.error.code}] ${response.error.message}`)
            );
          } else {
            pending.resolve(response.result);
          }
        }
      } catch (e) {
        this.emit("error", new Error(`Invalid JSON response: ${line}`));
      }
    }
  }
}
