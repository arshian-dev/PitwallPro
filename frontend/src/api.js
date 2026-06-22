const API = import.meta.env.DEV ? 'http://localhost:8000' : '/_/backend';

export async function fetchJSON(path) {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

export default API;
