import { createConnection, Socket } from "net";
import { EventEmitter } from "events";
import { spawn, ChildProcess } from "child_process";
import * as path from "path";

interface PythonBridgeOptions {
  port: number;
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

  constructor(options: PythonBridgeOptions) {
    super();
    this.options = {
      timeout: 60000,
      ...options,
    };
  }

  async start(): Promise<void> {
    // Start the Python bridge process
    this.process = spawn("python3", [this.options.bridgeScript], {
      stdio: ["pipe", "pipe", "pipe"],
      cwd: path.dirname(this.options.bridgeScript),
    });

    this.process.stdout?.on("data", (data) => {
      console.log(`[Bridge stdout]: ${data}`);
    });

    this.process.stderr?.on("data", (data) => {
      console.error(`[Bridge stderr]: ${data}`);
    });

    this.process.on("exit", (code) => {
      console.log(`Bridge process exited with code ${code}`);
      this.connected = false;
      this.emit("disconnected");
    });

    // Wait for the socket to be ready
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Connect to the socket
    await this.connect();
  }

  private async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const maxRetries = 10;
      let retries = 0;

      const tryConnect = () => {
        this.socket = createConnection({ host: '127.0.0.1', port: this.options.port });

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
        });
      };

      tryConnect();
    });
  }

  async stop(): Promise<void> {
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
    if (!this.socket || !this.connected) {
      throw new Error("Not connected");
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
