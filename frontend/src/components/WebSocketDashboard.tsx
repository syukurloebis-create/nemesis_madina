import { useEffect, useState } from "react";

export default function WebSocketDashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8001/ws/debug");

    ws.onmessage = (e) => {
      setData(JSON.parse(e.data));
    };

    return () => ws.close();
  }, []);

  if (!data) return <div>loading...</div>;

  return (
    <div style={{ padding: 20 }}>
      <h2>🧠 NEMESIS WS OBSERVABILITY</h2>

      <p>Connections: {data.data.connections}</p>

      <h3>Recent Events</h3>
      <pre>
        {JSON.stringify(data.data.recent_events, null, 2)}
      </pre>

      <h3>Errors</h3>
      <pre>
        {JSON.stringify(data.data.recent_errors, null, 2)}
      </pre>
    </div>
  );
}