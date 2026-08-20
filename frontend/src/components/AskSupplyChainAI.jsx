import React, { useState, useRef, useEffect } from 'react';
import './AskSupplyChainAI.css';

export default function AskSupplyChainAI({ onTriggerSimulation, contextState }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: 'Hey! I\'m your supply chain assistant. Ask me anything about the disruption — like "Why not just use Supplier B?" or "What if the port stays closed?"'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, isOpen]);

  // Call the real backend!
  const fetchLiveResponse = async (messagesArray) => {
    try {
      const payload = {
        messages: messagesArray,
        context: contextState || {
          beta: 0.5,
          adoption: 0.5,
          naiveKPI: { cost: 12000000, sla: 20 },
          aiKPI: { cost: 3000000, sla: 4 },
          useOptions: false
        }
      };
      
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error('API Error');
      return await response.json();
    } catch (e) {
      console.error('Chat API failed, falling back to basic error message:', e);
      return {
        text: 'The connection to the AI Engine timed out. Please check the backend server.'
      };
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const newMsg = {
      id: Date.now(),
      sender: 'user',
      text: inputValue
    };
    
    const updatedMessages = [...messages, newMsg];
    setMessages(updatedMessages);
    setInputValue('');
    setIsTyping(true);

    // Call live backend
    try {
      const response = await fetchLiveResponse(updatedMessages);
      setIsTyping(false);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        text: response.text,
        action: response.action
      }]);
    } catch (e) {
      setIsTyping(false);
    }
  };

  const handleActionClick = (action) => {
    if (action.type === 'trigger_ai') {
      if (onTriggerSimulation) {
        onTriggerSimulation();
      }
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'ai',
        text: 'Done! Check the dashboard above — the AI has redistributed shipments across suppliers. Compare the "Without AI" and "With AI" panels to see the difference.'
      }]);
    }
  };

  if (!isOpen) {
    return (
      <div className="chat-widget-container">
        <button className="chat-toggle-btn" onClick={() => setIsOpen(true)}>
          <span style={{ display: 'none' }}></span> Ask SupplyChainAI
        </button>
      </div>
    );
  }

  return (
    <div className="chat-widget-container">
      <div className="chat-window">
        <div className="chat-header">
          <div className="chat-title">
            <span style={{ display: 'none' }}></span> Ask SupplyChainAI
          </div>
          <button className="chat-close" onClick={() => setIsOpen(false)}>×</button>
        </div>
        
        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              <div className="message-sender">
                {msg.sender === 'user' ? 'Procurement Manager' : 'SupplyChainAI'}
              </div>
              <div className="message-bubble">
                {msg.text}
              </div>
              {msg.action && (
                <button 
                  className="chat-action-btn"
                  onClick={() => handleActionClick(msg.action)}
                >
                  {msg.action.label}
                </button>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="typing-dots">
              <span></span><span></span><span></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSend}>
          <input
            type="text"
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about the recommendation..."
          />
          <button 
            type="submit" 
            className="chat-send"
            disabled={!inputValue.trim() || isTyping}
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  );
}
