import { EventEmitter } from "events";
interface PythonBridgeOptions {
    port: number;
    bridgeScript: string;
    timeout?: number;
}
export declare class PythonBridge extends EventEmitter {
    private socket;
    private process;
    private options;
    private actualPort;
    private requestId;
    private pendingRequests;
    private buffer;
    private connected;
    private reconnecting;
    private shouldReconnect;
    private restarting;
    private processExitedUnexpectedly;
    constructor(options: PythonBridgeOptions);
    start(): Promise<void>;
    private connect;
    private scheduleReconnect;
    private scheduleRestart;
    private ensureConnected;
    stop(): Promise<void>;
    call<T>(method: string, params: Record<string, unknown>): Promise<T>;
    isConnected(): boolean;
    private handleData;
}
export {};
