import React, { useEffect, useRef, useState } from "react";
import "./DemoApp.css";

function ChatBox() {
  const [messages, setMessages] = useState([
    { id: 1, role: "bot", text: "Hey! Ask me anything." }
  ]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const listRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isSending) return;

    setIsSending(true);

    const userMsg = { id: crypto.randomUUID(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // Simulate bot response
    await new Promise((r) => setTimeout(r, 500));
    const botMsg = {
      id: crypto.randomUUID(),
      role: "bot",
      text: `Thanks for your message! You said: "${text}"`
    };

    setMessages((prev) => [...prev, botMsg]);

    setIsSending(false);
    inputRef.current?.focus();
  };

  return (
    <div className="chatbox-area">
      <div ref={listRef} className="chatbox-messages">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`chatbox-bubble ${m.role === "user" ? "user" : "bot"}`}
          >
            {m.text}
          </div>
        ))}
      </div>

      <form
        className="chatbox-composer"
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
      >
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Type a message..."
          rows={1}
        />
        <button type="submit" disabled={isSending || !input.trim()}>
          {isSending ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

const DemoApp = () => {
  return (
    <div className="demo-app">
      <div className="demo-header">
        <h1>Hack Attack Business</h1>
        <h2>Curated for all your business needs</h2>
      </div>

      <div className="chatbox">
        <div className="chatbox-header">AI Assistant</div>
        <ChatBox />
      </div>
    </div>
  );
};

export default DemoApp;