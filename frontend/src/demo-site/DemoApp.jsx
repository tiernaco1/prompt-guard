import React, {useEffect, useRef, useState} from "react";

function ChatBox(){
    const [messages, setMessages] = useState([
        {id: 1, role: "bot", text: "Hey! Ask me anything."}
    ]);

    const [input, setInput] = useState("");
    const [isSending, setIsSending] = useState(false);

    const listRef = useRef(null);
    const inputRef = useRef(null);


    const sendMessage = async () => {
        const text = input.trim();
        if (!text || isSending) return;

        setIsSending(true);

        const userMsg = {id: crypto.randomUUID(), role: "user", text};
        setMessages((prev) => [...prev, userMsg]);
        setInput("");

        // 2) Optional: replace this with your API call
    //    Example: const reply = await fetch("/api/chat", ...)
        await new Promise((r) => setTimeout(r, 300));
        const botMsg = {
        id: crypto.randomUUID(),
        role: "bot",
        text: `You said: ${text}`,
        };

        setMessages((prev) => [...prev, botMsg]);

        setIsSending(false);
        inputRef.current?.focus();

        return(
            <div className = "chatbox-area">
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
                        placeholder="Type a message..."
                        rows={1}
                    />
                    <button type="submit" disabled={isSending || !input.trim()}>
                        Send
                    </button>
                </form>
            </div>
        );
    };
};

const DemoApp = () => {
    return (
        <div>
            <h1>Hack Attack Business</h1>
            <h2>Curated for all your business needs</h2>

            <div className = "chatbox">
                <ChatBox />
            </div>
        </div>
    );
}

export default DemoApp