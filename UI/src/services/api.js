// API service for Contract Analysis chat
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Send a question to the RAG backend.
 * @param {string} query - User's question
 * @returns {Promise<{ answer: string, sources: any }>}
 */
export async function sendMessage(query) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to get response from server");
  }

  return response.json(); // returns { answer: "...", sources: [...] }
}

/* new api */

/**
 * Fetch the list of uploaded contract files.
 * @returns {Promise<string[]>}
 */
export async function fetchDocuments() {
  const response = await fetch(`${BASE_URL}/files`);

  if (!response.ok) {
    throw new Error("Failed to fetch documents");
  }

  const data = await response.json();
  return data.files; // backend returns { files: ["filename", ...] }
}
