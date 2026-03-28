export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`msg-row ${isUser ? 'user' : 'ai'}`}>
      <div className={`msg-av ${isUser ? 'user' : 'ai'}`}>
        {isUser ? 'You' : 'AI'}
      </div>
      <div className={`msg-bub ${isUser ? 'user' : 'ai'}`}>
        {message.content}
      </div>
    </div>
  );
}
