import { useState, useRef, useEffect } from 'react';

const SendIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

export default function ChatInput({ onSend, loading }) {
  const [text, setText] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }, [text]);

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setText('');
    if (ref.current) ref.current.style.height = 'auto';
  };

  return (
    <div className="chat-inp-wrap">
      <div className="chat-inp-box">
        <textarea
          ref={ref}
          className="chat-textarea"
          rows={1}
          value={text}
          placeholder="Ask anything about your contracts…  (Enter to send)"
          disabled={loading}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
          }}
        />
        <button
          className="chat-send-btn"
          onClick={submit}
          disabled={!text.trim() || loading}
          title="Send"
        >
          <SendIcon/>
        </button>
      </div>
      <p className="chat-hint">Enter to send · Shift+Enter for new line</p>
    </div>
  );
}
