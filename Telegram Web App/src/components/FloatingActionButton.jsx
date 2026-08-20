/**
 * FloatingActionButton — Persistent Chat Trigger
 * =================================================
 * A pulsing gold FAB fixed above the bottom navigation.
 * Tapping opens/closes the AI Concierge chat drawer.
 */

import React from "react";
import { MessageCircle, X } from "lucide-react";
import { useChat } from "../context/ChatContext";
import { useTenant } from "../context/TenantContext";

export default function FloatingActionButton() {
  const { isOpen, toggleChat, messages } = useChat();
  const { colors } = useTenant();

  // Count unread AI messages (simple heuristic: messages from assistant after last user message)
  const unreadCount = 0; // In a real app, track read state

  return (
    <>
      <style>{`
        @keyframes fab-pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(201, 162, 39, 0.4); }
          50% { box-shadow: 0 0 0 12px rgba(201, 162, 39, 0); }
        }
        @keyframes fab-scale-in {
          from { transform: scale(0) rotate(-180deg); opacity: 0; }
          to { transform: scale(1) rotate(0deg); opacity: 1; }
        }
        .fab-btn {
          animation: fab-pulse 3s ease-in-out infinite;
          transition: all 240ms cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .fab-btn:hover {
          transform: scale(1.08);
          animation: none;
        }
        .fab-btn:active {
          transform: scale(0.95);
        }
        .fab-btn.is-open {
          animation: none;
          background: var(--color-surface-hi) !important;
          border-color: var(--color-border-hi) !important;
        }
        .fab-icon {
          animation: fab-scale-in 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
        }
      `}</style>

      <button
        onClick={toggleChat}
        className={`fab-btn fixed z-30 flex items-center justify-center rounded-full ${isOpen ? "is-open" : ""}`}
        style={{
          bottom: 72,
          right: 16,
          width: 52,
          height: 52,
          background: isOpen ? colors.surfaceHi : colors.gold,
          border: `2px solid ${isOpen ? colors.borderHi : colors.goldBright}`,
          cursor: "pointer",
        }}
        aria-label={isOpen ? "Закрыть консьерж" : "Открыть консьерж"}
      >
        <span className="fab-icon" key={isOpen ? "close" : "open"}>
          {isOpen ? (
            <X size={22} color={colors.textMuted} strokeWidth={2} />
          ) : (
            <MessageCircle size={22} color="#1A1508" strokeWidth={2} />
          )}
        </span>

        {/* Unread badge */}
        {!isOpen && unreadCount > 0 && (
          <span
            className="absolute -top-1 -right-1 flex items-center justify-center rounded-full"
            style={{
              width: 18,
              height: 18,
              background: colors.accentDanger,
              fontSize: 10,
              fontWeight: 700,
              color: "#fff",
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>
    </>
  );
}
