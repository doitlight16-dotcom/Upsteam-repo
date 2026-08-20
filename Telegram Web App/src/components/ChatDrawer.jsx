/**
 * ChatDrawer — AI Concierge Chat Overlay
 * ========================================
 * Slide-up panel with message bubbles, quick-action chips,
 * and text input. Communicates with backend via ChatContext.
 */

import React, { useState, useRef, useEffect } from "react";
import {
  X,
  Send,
  Calendar,
  Car,
  TrendingUp,
  AlertTriangle,
  Bot,
  Sparkles,
} from "lucide-react";
import { useChat } from "../context/ChatContext";
import { useTenant } from "../context/TenantContext";

const QUICK_ACTIONS = [
  { label: "📅 Моё расписание", message: "Какие мероприятия у меня сегодня?" },
  { label: "🚗 Вызвать авто", message: "Какие машины сейчас доступны? Подберите ближайшую." },
  { label: "📊 Инвест-лоты", message: "Покажите доступные инвестиционные лоты и их ROI." },
  { label: "🆘 SOS", message: "SOS! Мне нужна экстренная помощь координатора." },
];

export default function ChatDrawer() {
  const { messages, isOpen, isLoading, sendMessage, closeChat } = useChat();
  const { colors, fonts, tenant } = useTenant();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  // Focus input when drawer opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 350);
    }
  }, [isOpen]);

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (msg) => {
    sendMessage(msg);
  };

  if (!isOpen) return null;

  return (
    <>
      <style>{`
        @keyframes drawer-slide-up {
          from { transform: translateY(100%); opacity: 0.5; }
          to { transform: translateY(0); opacity: 1; }
        }
        @keyframes drawer-backdrop-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes typing-dot {
          0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
          30% { opacity: 1; transform: translateY(-4px); }
        }
        .chat-drawer-backdrop {
          animation: drawer-backdrop-in 200ms ease forwards;
        }
        .chat-drawer-panel {
          animation: drawer-slide-up 320ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .typing-dot {
          animation: typing-dot 1.4s ease-in-out infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.15s; }
        .typing-dot:nth-child(3) { animation-delay: 0.3s; }
        .msg-bubble {
          animation: drawer-slide-up 200ms ease forwards;
        }
      `}</style>

      {/* Backdrop */}
      <div
        className="chat-drawer-backdrop fixed inset-0 z-40"
        style={{ background: "rgba(10, 9, 7, 0.6)" }}
        onClick={closeChat}
      />

      {/* Panel */}
      <div
        className="chat-drawer-panel fixed bottom-0 left-0 right-0 z-50 flex flex-col"
        style={{
          height: "82vh",
          maxHeight: 680,
          background: colors.bg,
          borderTop: `1px solid ${colors.borderHi}`,
          borderRadius: "24px 24px 0 0",
          boxShadow: "0 -10px 60px rgba(0, 0, 0, 0.5)",
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-5 py-3.5 shrink-0"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center"
              style={{ background: `${colors.gold}18`, border: `1px solid ${colors.gold}33` }}
            >
              <Sparkles size={16} color={colors.gold} />
            </div>
            <div>
              <div
                style={{
                  fontFamily: fonts.body,
                  fontSize: 14,
                  fontWeight: 600,
                  color: colors.text,
                }}
              >
                AI Консьерж
              </div>
              <div
                style={{
                  fontFamily: fonts.mono,
                  fontSize: 10,
                  color: colors.textFaint,
                  letterSpacing: 1,
                }}
              >
                {tenant.brand_name}
              </div>
            </div>
          </div>
          <button
            onClick={closeChat}
            className="p-1.5 rounded-lg"
            style={{ background: colors.surfaceHi }}
            aria-label="Закрыть чат"
          >
            <X size={16} color={colors.textMuted} />
          </button>
        </div>

        {/* Messages Area */}
        <div
          className="flex-1 overflow-y-auto px-4 py-4"
          style={{ scrollbarWidth: "none" }}
        >
          {/* Welcome message if empty */}
          {messages.length === 0 && (
            <div className="text-center py-6">
              <div
                className="w-14 h-14 rounded-full mx-auto flex items-center justify-center mb-4"
                style={{
                  background: `${colors.gold}14`,
                  border: `1px solid ${colors.border}`,
                }}
              >
                <Bot size={24} color={colors.gold} strokeWidth={1.5} />
              </div>
              <div
                style={{
                  fontFamily: fonts.display,
                  fontSize: 17,
                  color: colors.text,
                  fontStyle: "italic",
                }}
              >
                Добро пожаловать
              </div>
              <div
                style={{
                  fontFamily: fonts.body,
                  fontSize: 12.5,
                  color: colors.textMuted,
                  marginTop: 6,
                  lineHeight: 1.5,
                  maxWidth: 260,
                  marginLeft: "auto",
                  marginRight: "auto",
                }}
              >
                Я ваш цифровой консьерж. Спросите меня о расписании, трансфере, инвестициях или нажмите быструю кнопку ниже.
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap gap-2 justify-center mt-5">
                {QUICK_ACTIONS.map((qa) => (
                  <button
                    key={qa.label}
                    onClick={() => handleQuickAction(qa.message)}
                    className="px-3 py-1.5 rounded-full"
                    style={{
                      background: colors.surface,
                      border: `1px solid ${colors.border}`,
                      fontFamily: fonts.body,
                      fontSize: 12,
                      color: colors.text,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {qa.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message Bubbles */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`msg-bubble flex mb-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className="px-3.5 py-2.5 rounded-2xl max-w-[85%]"
                style={{
                  background: msg.role === "user"
                    ? `${colors.gold}1A`
                    : colors.surface,
                  border: `1px solid ${msg.role === "user" ? `${colors.gold}44` : colors.border}`,
                  borderBottomRightRadius: msg.role === "user" ? 6 : 18,
                  borderBottomLeftRadius: msg.role === "user" ? 18 : 6,
                }}
              >
                <div
                  style={{
                    fontFamily: fonts.body,
                    fontSize: 13,
                    color: msg.isError ? colors.accentDanger : colors.text,
                    lineHeight: 1.55,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex justify-start mb-3">
              <div
                className="px-4 py-3 rounded-2xl flex items-center gap-1.5"
                style={{
                  background: colors.surface,
                  border: `1px solid ${colors.border}`,
                  borderBottomLeftRadius: 6,
                }}
              >
                <span
                  className="typing-dot inline-block w-2 h-2 rounded-full"
                  style={{ background: colors.gold }}
                />
                <span
                  className="typing-dot inline-block w-2 h-2 rounded-full"
                  style={{ background: colors.gold }}
                />
                <span
                  className="typing-dot inline-block w-2 h-2 rounded-full"
                  style={{ background: colors.gold }}
                />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions (shown when there are messages) */}
        {messages.length > 0 && (
          <div
            className="px-4 py-2 flex gap-2 overflow-x-auto shrink-0"
            style={{ borderTop: `1px solid ${colors.border}`, scrollbarWidth: "none" }}
          >
            {QUICK_ACTIONS.map((qa) => (
              <button
                key={qa.label}
                onClick={() => handleQuickAction(qa.message)}
                disabled={isLoading}
                className="px-3 py-1.5 rounded-full shrink-0"
                style={{
                  background: colors.surface,
                  border: `1px solid ${colors.border}`,
                  fontFamily: fonts.body,
                  fontSize: 11,
                  color: colors.textMuted,
                  whiteSpace: "nowrap",
                  opacity: isLoading ? 0.5 : 1,
                }}
              >
                {qa.label}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <div
          className="px-4 py-3 shrink-0 flex items-center gap-2"
          style={{
            borderTop: `1px solid ${colors.border}`,
            background: colors.surface,
            borderRadius: "0 0 0 0",
          }}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Напишите вопрос…"
            disabled={isLoading}
            className="flex-1 bg-transparent outline-none"
            style={{
              fontFamily: fonts.body,
              fontSize: 14,
              color: colors.text,
              caretColor: colors.gold,
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="w-9 h-9 rounded-full flex items-center justify-center shrink-0 transition-all"
            style={{
              background: input.trim() && !isLoading ? colors.gold : colors.surfaceHi,
              opacity: input.trim() && !isLoading ? 1 : 0.5,
            }}
            aria-label="Отправить"
          >
            <Send
              size={15}
              color={input.trim() && !isLoading ? "#1A1508" : colors.textFaint}
              strokeWidth={2}
            />
          </button>
        </div>
      </div>
    </>
  );
}
