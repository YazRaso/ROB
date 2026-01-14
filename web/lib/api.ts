const BASE_URL = "http://localhost:8000";

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
    }
};
