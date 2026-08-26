import { API_BASE, ApiError } from "./client";
import type { ChatResponse, ChatScanResult } from "../types/chatbot";

const CHAT_ENDPOINT = `${API_BASE}/chatbot/chat`;

export class ChatAPIError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ChatAPIError";
  }
}

async function parseChatResponse(response: Response): Promise<ChatResponse> {
  let data: { detail?: string; reply?: string } & Partial<ChatResponse>;

  try {
    data = (await response.json()) as typeof data;
  } catch {
    throw new ChatAPIError(
      "Received an invalid response from the server.",
      response.status,
    );
  }

  if (!response.ok) {
    throw new ChatAPIError(
      data.detail ||
        "The chatbot service encountered an error. Please try again.",
      response.status,
    );
  }

  if (!data.reply) {
    throw new ChatAPIError(
      "The chatbot returned an empty response.",
      response.status,
    );
  }

  return data as ChatResponse;
}

interface ChatPostBody {
  message?: string;
  conversation_id?: string | null;
  scan_result?: ChatScanResult;
}

async function postChat(body: ChatPostBody): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ChatAPIError(
      "Unable to reach the chatbot service. Please check your connection and try again.",
      0,
    );
  }

  return parseChatResponse(response);
}

export async function sendChatMessage(
  message: string,
  conversationId: string | null = null,
): Promise<ChatResponse> {
  return postChat({
    message,
    conversation_id: conversationId,
  });
}

export async function sendScanResult(
  scanResult: ChatScanResult,
  conversationId: string | null = null,
): Promise<ChatResponse> {
  return postChat({
    scan_result: scanResult,
    conversation_id: conversationId,
  });
}

export async function clearConversation(
  conversationId: string,
): Promise<boolean> {
  if (!conversationId) {
    return false;
  }

  try {
    const response = await fetch(`${CHAT_ENDPOINT}/${conversationId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      return false;
    }

    const data = (await response.json()) as { cleared?: boolean };
    return Boolean(data.cleared);
  } catch {
    return false;
  }
}

export async function checkChatbotHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/chatbot/health`);
    if (!response.ok) {
      return false;
    }

    const data = (await response.json()) as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}

export { ApiError };
