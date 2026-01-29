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
    private requestId;
    private pendingRequests;
    private buffer;
    private connected;
    constructor(options: PythonBridgeOptions);
    start(): Promise<void>;
    private connect;
    stop(): Promise<void>;
    call<T>(method: string, params: Record<string, unknown>): Promise<T>;
    isConnected(): boolean;
    private handleData;
}
export {};
