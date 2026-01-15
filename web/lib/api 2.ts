const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EventSource = "drive" | "repo" | "telegram";

export interface DataEvent {
    source: EventSource;
    timestamp: string;
    client_id?: string;
}

export const API = {
    async getStatus(clientId: string = "default_user") {
        const res = await fetch(`${BASE_URL}/system/status?client_id=${clientId}`);
        if (!res.ok) throw new Error("Failed to fetch status");
        return res.json();
    },

    async getActivity(clientId: string = "default_user") {
        const res = await fetch(`${BASE_URL}/activity?client_id=${clientId}`);
        if (!res.ok) throw new Error("Failed to fetch activity");
        return res.json();
    },

    async query(prompt: string, clientId: string = "default_user") {
        // Check for tool invocations and use API route if found
        const toolPattern = /@(\w+)/;
        if (toolPattern.test(prompt)) {
            // Use Next.js API route for tool handling
            const res = await fetch("/api/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt, clientId }),
            });
            if (!res.ok) throw new Error("Failed to query");
            const data = await res.json();
            
            // Handle tool results
            if (data.type === "tool_result") {
                if (data.tool === "create_file") {
                    // For web, we could trigger file download or show content
                    return data.reply + "\n\n" + JSON.stringify(data.result, null, 2);
                }
                return data.reply || data.result?.formatted || JSON.stringify(data.result);
            }
            
            return data.reply || data;
        }
        
        // Normal query - use direct backend
        const res = await fetch(`${BASE_URL}/messages/send?client_id=${clientId}&content=${encodeURIComponent(prompt)}`, {
            method: "POST",
        });
        if (!res.ok) throw new Error("Failed to query");
        return res.text(); // Current backend returns text
    },

    async authenticateDrive() {
        const res = await fetch(`${BASE_URL}/drive/authenticate`, { method: "POST" });
        if (!res.ok) throw new Error("Failed to authenticate drive");
        return res.json();
    },

    async registerDriveDocument(clientId: string, url: string) {
        const res = await fetch(`${BASE_URL}/drive/register?client_id=${clientId}&drive_url=${encodeURIComponent(url)}`, {
            method: "POST",
        });
        if (!res.ok) throw new Error("Failed to register document");
        return res.json();
    },

    subscribeToEvents(onEvent: (event: DataEvent) => void): () => void {
        const eventSource = new EventSource(`${BASE_URL}/events`);

        eventSource.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data) as DataEvent;
                onEvent(data);
            } catch (err) {
                console.error("Failed to parse event:", err);
            }
        };

        eventSource.onerror = (err) => {
            console.error("SSE connection error:", err);
        };

        // Return cleanup function
        return () => eventSource.close();
    }
};
