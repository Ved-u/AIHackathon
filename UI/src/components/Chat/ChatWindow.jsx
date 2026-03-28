import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput   from './ChatInput';
import { sendMessage } from '../../services/api';

const CHIPS = [
  'Summarise this contract',
  'What are the payment terms?',
  'List all termination clauses',
  'Key obligations of each party',
  'Are there any risks I should know?',
  'Who owns the intellectual property?',
];

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [view,     setView]     = useState('welcome'); // 'welcome' | 'chat'
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    if (!text.trim() || loading) return;
    setView('chat');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const data = await sendMessage(text);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer || data.response || 'wrong',
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error: ${err.message}`,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const startNew = () => {
    if (loading) return;
    setMessages([]);
    setView('welcome');
  };

  return (
    <div className="chat-win">
      {view === 'chat' && (
        <div className="chat-toolbar">
          <button className="new-chat-btn" onClick={startNew} title="Start a new chat">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 5H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7"/>
              <path d="M18.375 2.625a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4Z"/>
            </svg>
            New Chat
          </button>
        </div>
      )}
      <div className="chat-scroll">
        {view === 'welcome' ? (
          <div className="chat-welcome">
            <div className="chat-welcome-ring">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h2>Contract Analysis AI</h2>
            {messages.length > 0 && (
              <button className="continue-chat-btn" onClick={() => setView('chat')}>
                Continue conversation →
              </button>
            )}
            <div className="chat-chips">
              {CHIPS.map(c => (
                <button key={c} className="chat-chip" onClick={() => send(c)}>{c}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-msgs">
            {messages.map((m, i) => <ChatMessage key={i} message={m} />)}
            {loading && (
              <div className="msg-row ai">
                <div className="msg-av ai">AI</div>
                <div className="typing-bub">
                  <span className="dot"/><span className="dot"/><span className="dot"/>
                </div>
              </div>
            )}
            <div ref={bottomRef}/>
          </div>
        )}
      </div>
      <ChatInput onSend={send} loading={loading} />
    </div>
  );
}
