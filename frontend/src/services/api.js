const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";

const request = async (path, payload) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(
      detail?.message || `Pedido falhou com estado ${response.status}.`,
    );
  }

  return response.json();
};

export const apiConfig = {
  apiBaseUrl: API_BASE_URL,
};

export const depositVault = (payload) => request("/api/deposit", payload);

export const openVault = (payload) => request("/api/open", payload);

// `tamper-demo` endpoint removed; no tamper helper exported.
