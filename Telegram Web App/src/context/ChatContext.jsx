/**
 * ChatContext — AI Concierge State Management
 * =============================================
 * Manages chat messages, open/close state, and API communication
 * for the AI concierge overlay.
 *
 * Usage:
 *   const { messages, isOpen, isLoading, sendMessage, toggleChat } = useChat();
 */

import React, { createContext, useContext, useState, useCallback, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "";

const ChatContext = createContext({
  messages: [],
  isOpen: false,
  isLoading: false,
  sendMessage: () => {},
  toggleChat: () => {},
  closeChat: () => {},
  clearChat: () => {},
});

export function useChat() {
  return useContext(ChatContext);
}

export function ChatProvider({ tenantId = "default", children }) {
  const [messages, setMessages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesRef = useRef(messages);
  messagesRef.current = messages;

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = { role: "user", content: text.trim() };
    const updatedMessages = [...messagesRef.current, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/concierge/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: updatedMessages.map((m) => ({ role: m.role, content: m.content })),
          tenant_id: tenantId,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const aiMessage = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Concierge chat error:", err);
      const errorMessage = {
        role: "assistant",
        content: "⚠️ Извините, произошла ошибка при обработке запроса. Попробуйте ещё раз или свяжитесь с координатором.",
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [tenantId, isLoading]);

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <ChatContext.Provider
      value={{ messages, isOpen, isLoading, sendMessage, toggleChat, closeChat, clearChat }}
    >
      {children}
    </ChatContext.Provider>
  );
}
