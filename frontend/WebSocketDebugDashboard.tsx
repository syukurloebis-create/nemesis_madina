import { useEffect, useRef, useState } from "react";

interface WSLog {
  type: string;
  status?: string;
  payload?: any;
  client_id?: string;
  ts?: number;
}

export default function WebSocketDebugDashboard() {
  const [logs, setLogs] = useState<WSLog[]>([]);
  const [status, setStatus] = useState("DISCONNECTED");

  const wsRef = useRef<WebSocket | null>(null);
  const connectCountRef = useRef(0);

  useEffect(() => {
    connectCountRef.current += 1;

    const ws = new WebSocket("ws://localhost:8001/ws/replay");
    wsRef.current = ws;

    console.log("🔌 WS INIT COUNT:", connectCountRef.current);

    ws.onopen = () => {
      console.log("WS RAW OPEN (NOT RELIABLE YET)");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 🔥 REAL CONNECT VALIDATION
        if (data.type === "SYSTEM" && data.status === "CONNECTED") {
          setStatus("CONNECTED");
          console.log("✅ VERIFIED CONNECT:", data.client_id);
        }

        setLogs((prev) => [data, ...prev].slice(0, 100));
      } catch (e) {
        console.error("Parse error:", e);
      }
    };

    ws.onerror = (e) => {
      setStatus("ERROR");
      console.error("WS ERROR", e);
    };

    ws.onclose = () => {
      setStatus("DISCONNECTED");
      console.warn("WS CLOSED");
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div style={{ padding: 20, fontFamily: "monospace" }}>
      <h2>🔥 WebSocket Debug Reality Check</h2>

      <div>
        Status:{" "}
        <b style={{ color: status === "CONNECTED" ? "green" : "red" }}>
          {status}
        </b>
      </div>

      <div style={{ marginTop: 10 }}>
        <b>Connect Counter:</b> {connectCountRef.current}
      </div>

      <hr />

      <div>
        {logs.map((log, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <span style={{ color: "blue" }}>{log.type}</span>{" "}
            {log.status && <b>({log.status})</b>}
            {log.client_id && <div>client: {log.client_id}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}