const API = 'http://localhost:8000';

export async function fetchJSON(path) {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

export default API;
