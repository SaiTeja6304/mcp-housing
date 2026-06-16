import type { ChatMessagePayload, ChatResponse } from './types';

const API_BASE = 'http://127.0.0.1:8000';

export async function sendChatMessage(message: string, history: ChatMessagePayload[]): Promise<string> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      history,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${response.statusText}`);
  }

  const data: ChatResponse = await response.json();
  return data.response;
}
