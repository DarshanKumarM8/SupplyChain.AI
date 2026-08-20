from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
import random

router = APIRouter()
logger = logging.getLogger(__name__)

# Try to initialize OpenAI client if API key is present
client = None
try:
    from openai import AsyncOpenAI
    if os.environ.get("OPENAI_API_KEY"):
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    pass

class Message(BaseModel):
    id: int
    sender: str
    text: str
    action: Optional[Dict[str, Any]] = None

class ContextState(BaseModel):
    beta: float
    adoption: float
    naiveKPI: Dict[str, Any]
    aiKPI: Dict[str, Any]
    useOptions: bool

class ChatRequest(BaseModel):
    messages: List[Message]
    context: ContextState

class ActionResponse(BaseModel):
    label: str
    type: str

class ChatResponseFormat(BaseModel):
    text: str
    action: Optional[ActionResponse] = None

SYSTEM_PROMPT = """
You are a friendly supply chain assistant for SupplyChainAI. You help procurement managers understand supply chain disruptions in simple, plain English.

CONTEXT: A typhoon has shut down Kaohsiung Port. The system is simulating what happens when companies panic and all rush to the same backup supplier.

Current simulation state:
{context_str}

RULES:
1. Speak in simple, everyday language. No jargon. Imagine you're explaining to someone who has never worked in supply chain.
2. Use short sentences. Be warm and helpful, like a smart colleague.
3. When explaining why Supplier B is bad: "If everyone rushes to the same backup, it gets overwhelmed — like everyone trying to exit through one door."
4. If the user wants to run a simulation, include an action object.
5. Never say "equilibrium", "Monte Carlo", "Fokker-Planck", "least-regret", or "meta-herd". Use plain words instead.
"""

def get_smart_mock_response(text: str) -> dict:
    """Friendly, plain-English fallback responses."""
    lower = text.lower().strip()

    # Greetings
    if lower in ['hi', 'hello', 'hey', 'hey there', 'hii', 'hiii']:
        return {
            "text": "Hey! 👋 I'm your supply chain assistant. I can help you understand what happens when a disruption hits — like the typhoon shutting down Kaohsiung Port right now. Try asking me things like 'What if I stop using Supplier A?' or 'Why not just use Supplier B?'"
        }

    # What can you do
    if 'what can you do' in lower or 'what do you do' in lower or 'help' in lower:
        return {
            "text": "I can help you understand how supply chain disruptions play out! For example:\n\n• 'What if the port stays closed for 10 more days?'\n• 'Why shouldn't I just use Supplier B?'\n• 'What's the cheapest option?'\n• 'What if I stop using Supplier A?'\n\nJust ask anything about the disruption, and I'll break it down for you."
        }

    # Supplier B
    if 'supplier b' in lower or "why not" in lower or "why didn't" in lower or 'why not just' in lower:
        return {
            "text": "Great question! Supplier B looks like the obvious backup — it's close and usually reliable. But here's the problem: when a port shuts down, *everyone* rushes to Supplier B. It's like a traffic jam — if all cars take the same detour, that road gets jammed too.\n\nOur AI spreads orders across multiple suppliers (B, C, and even air freight) so no single one gets overwhelmed. That's why the AI side keeps deliveries at 96% while the panic side drops to 77%.",
            "action": {"label": "▶ Show this in the simulation", "type": "trigger_ai"}
        }

    # Supplier A
    if 'supplier a' in lower or "dont take supply" in lower or "don't take supply" in lower or "stop using" in lower:
        return {
            "text": "If you completely cut off Supplier A, your warehouse stock will run out in about 8 days. I'd recommend letting the AI redistribute that volume across your other suppliers — it'll find the best split automatically so you don't run dry.",
            "action": {"label": "▶ Run redistribution", "type": "trigger_ai"}
        }

    # Port closed / 10 days
    if '10 days' in lower or 'port' in lower or 'closed' in lower or 'shut down' in lower:
        return {
            "text": "If the port stays closed for 10 more days, your current stock won't last. You'd need to shift about 20% of shipments to air freight to keep deliveries on track. It costs more, but it prevents missed orders.",
            "action": {"label": "▶ Apply air freight shift", "type": "trigger_ai"}
        }

    # Cheapest
    if 'cheapest' in lower or 'cheap' in lower or 'cost' in lower or 'save money' in lower:
        return {
            "text": "The cheapest option is to send everything through Supplier B — it saves about 5% on shipping. But the risk is high: if too many other companies do the same, B gets overloaded and your deliveries drop to 72% on time. The AI's recommended split costs a tiny bit more but keeps deliveries at 96%."
        }

    # Confirmations
    if lower in ['sure', 'yes', 'ok', 'okay', 'do it', 'go ahead', 'run it', 'yep', 'yeah']:
        return {
            "text": "Running the simulation now! Watch the dashboard — you'll see how the AI spreads orders across suppliers to prevent any single one from getting overwhelmed. 🚀",
            "action": {"label": "▶ Show simulation", "type": "trigger_ai"}
        }

    # 80% / crowd
    if '80%' in lower or 'other buyers' in lower or 'other companies' in lower or 'everyone' in lower:
        return {
            "text": "When 80% of buyers rush to the same supplier, that supplier's capacity maxes out. Prices spike, lead times double, and deliveries drop. It's like a stampede — the AI avoids this by splitting orders smartly across multiple routes."
        }

    # How does it work
    if 'how does' in lower or 'how do' in lower or 'explain' in lower:
        return {
            "text": "Here's the simple version: when a disruption hits (like this typhoon), most companies panic and rush to the obvious backup. But if everyone picks the same backup, it gets overwhelmed.\n\nOur AI runs thousands of 'what-if' scenarios to find the smartest split — spreading orders across multiple suppliers so no single one breaks. That's why the AI side of the dashboard shows way better numbers than the panic side."
        }

    # Fallback - varied and friendly
    fallbacks = [
        "Good question! Based on what I'm seeing in the simulation, let me think about this... Would you like me to run a scenario with those constraints? Just say 'yes' and I'll show you what happens.",
        "Hmm, that's an interesting angle. I can model that for you — want me to run a quick simulation? You'll see the results update live on the dashboard.",
        "I'd love to explore that with you! Try rephrasing as a 'what if' question (like 'What if the port stays closed?') and I can give you specific numbers."
    ]
    return {
        "text": random.choice(fallbacks)
    }


@router.post("/ask")
async def ask_supply_chain_ai(request: ChatRequest):
    try:
        user_msg = next((m.text for m in reversed(request.messages) if m.sender == "user"), "")

        # If no OpenAI client, use the friendly mock
        if not client:
            logger.info("No OpenAI client available. Using friendly mock.")
            return get_smart_mock_response(user_msg)

        # Build context
        ctx = request.context
        context_str = f"- Market panic level: {ctx.beta} (0=calm, 1=maximum panic)\n- AI adoption rate: {ctx.adoption}\n- Cost without AI: ${ctx.naiveKPI.get('cost', 0):,}\n- Cost with AI: ${ctx.aiKPI.get('cost', 0):,}"

        system_content = SYSTEM_PROMPT.replace("{context_str}", context_str)

        api_messages = [{"role": "system", "content": system_content}]
        for msg in request.messages[-5:]:
            api_messages.append({
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.text
            })

        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=api_messages,
            response_format=ChatResponseFormat,
            temperature=0.4,
        )

        response_data = completion.choices[0].message.parsed

        return {
            "text": response_data.text,
            "action": response_data.action.model_dump() if response_data.action else None
        }

    except Exception as e:
        logger.error(f"Chat API Error: {str(e)}")
        user_msg = next((m.text for m in reversed(request.messages) if m.sender == "user"), "")
        return get_smart_mock_response(user_msg)
