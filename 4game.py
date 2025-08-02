import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Conversation Settings
MAX_HISTORY = 40
DELAY_BETWEEN_MESSAGES = 0.5
GAME_INSTRUCTION = "DISCOVERY MISSION: You have partial clues but the full puzzle has missing pieces. EXPLORE unknown relationships by proposing hypotheses H→. TEST theories through collaborative reasoning. ELIMINATE false ideas ✗. CONFIRM discoveries ✓. Question: What other ages, people, birds, positions exist? Develop symbols for your exploration process and findings."

# Agent Configurations
AGENTS = [
    {
        "name": "Agent 1",
        "model": "openai/gpt-4.1",
               "system_prompt": """Dr. Marcus - mathematical explorer who discovers through hypothesis testing. KNOWN FACTS: (19yr ← Oliver) ∧ (pigeon → Oliver). EXPLORE unknown relationships by proposing hypotheses H1→, H2→. Test them logically. Mark proven facts as ✓, refuted ideas as ✗. Question: What other ages exist? Who else lives where? Create discovery symbols.""",

        "temperature": 1.2,
        "max_tokens": 50,
        "color": "\033[95m"  # Purple
    },
    {
        "name": "Agent 2",
        "model": "openai/gpt-4.1",
                 "system_prompt": """Prof. Elena - logical detective who eliminates false theories. FACTS: (pigeon ∈ {pos1, pos5}) ∧ (Oliver = pos3). MISSION: Challenge assumptions, test hypotheses H→ rigorously. Discover hidden constraints through proof by contradiction. EXPLORE: Are there other birds? More people? Mark wrong theories ✗. Build elimination chains.""",


        "temperature": 0.7,
        "max_tokens": 50,
        "color": "\033[96m"  # Cyan
    },
    {
        "name": "Agent 3",
        "model": "openai/gpt-4.1",
               "system_prompt": """Alex - pattern discoverer who generates creative hypotheses. DATA: (Joshua = 19yr) ∧ (37yr → wren). EXPLORE connections others miss. Propose wild theories H→ then test systematically. DISCOVER: What ages are missing? Which positions empty? Create innovative notation for findings. Mark breakthroughs ✓.""",


        "temperature": 1.0,
        "max_tokens": 50,
        "color": "\033[93m"  # Yellow
    },
    {
        "name": "Agent 4",
        "model": "openai/gpt-4.1",
                 "system_prompt": """Dr. Kim - discovery coordinator who maps the unknown. INTEL: (owl → pos1) ∧ (Luke = pos3). COORDINATE hypothesis testing across team. Track what's proven ✓ vs unproven H→. EXPLORE gaps in knowledge systematically. Guide team toward hidden discoveries. Develop shared notation for exploration.""",


        "temperature": 0.9,
        "max_tokens": 50,
        "color": "\033[92m"  # Green
    }
]

# Global conversation history
conversation_history = []


def clean_response(text: str) -> str:
    """Clean up response text by removing extra whitespace and newlines."""
    return ' '.join(text.strip().replace('\n', ' ').replace('\r', ' ').split())


def generate_response(
    prompt: str,
    agent_config: Dict,
    history: List[Dict],
    admin_context: Optional[str] = None
) -> str:
    """Generate response for a specific agent."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Build messages with agent's personality and history
        messages = [{"role": "system", "content": agent_config["system_prompt"]}]

        # Add admin context if this is the first turn
        if admin_context and len(history) == 0:
            messages.append({"role": "system", "content": admin_context})

        # Add conversation history
        messages.extend(history[-MAX_HISTORY:])

        # Add current message
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": agent_config["model"],
            "messages": messages,
            "temperature": agent_config["temperature"],
            "max_tokens": agent_config["max_tokens"],
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        if "choices" in result and result["choices"]:
            return clean_response(result["choices"][0]["message"]["content"])
        return "I couldn't generate a response."

    except Exception as e:
        print(f"\n[Error] {agent_config['name']}: {type(e).__name__}: {e}")
        return "Sorry, I encountered an error."


def print_message(agent_name: str, message: str, color_code: str = "") -> None:
    """Print a formatted message from an agent."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    clean_msg = clean_response(message)
    print(f"{color_code}[{timestamp}] {agent_name}: {clean_msg}\033[0m")


def print_separator(char: str = "=", length: int = 70) -> None:
    """Print a separator line."""
    print(char * length)


def print_welcome() -> None:
    """Print welcome message."""
    print()
    print_separator()
    print("🧩 Logic Experts Collaboration 🧩")
    print_separator()

    # Print agent names with colors
    agent_names = " - ".join(f"{agent['color']}{agent['name']}\033[0m" for agent in AGENTS)
    print(f"\n{agent_names}")

    print("\nPress Ctrl+C to stop at any time")
    print_separator()


def run_conversation() -> None:
    """Run a conversation between four agents."""
    print(f"\n")
    print_separator()
    print("Starting endless conversation (Press Ctrl+C to stop)")
    print_separator()
    print()

    # Clear conversation history for new conversation
    conversation_history.clear()

    # Display admin instruction
    print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Admin: {GAME_INSTRUCTION}\033[0m")
    print_separator()
    print()

    # Add game instruction to all agents' initial context
    admin_instruction = f"[Admin Instruction]: {GAME_INSTRUCTION}"

    # Dr. Marcus starts the discovery mission
    current_message = "EXPLORATION: Share known facts, propose hypotheses H→ about unknowns. What can we discover together?"
    agent_index = 0
    turn = 0

    # Run until solved or reasonable limit
    max_turns = 100  # Allow time for logical language development
    while turn < max_turns:
        try:
            current_agent = AGENTS[agent_index]

            # Show typing indicator
            print(f"{current_agent['color']}[{current_agent['name']} is thinking...]\033[0m",
                  end="\r", flush=True)

            # Generate response
            response = generate_response(
                current_message,
                current_agent,
                conversation_history,
                admin_instruction if turn == 0 else None
            )

            # Clear typing indicator line
            print(" " * 80, end="\r")

            # Print the response
            print_message(current_agent['name'], response, current_agent['color'])

            # Update conversation history
            conversation_history.extend([
                {"role": "user", "content": current_message},
                {"role": "assistant", "content": response}
            ])

            # Prepare for next turn
            current_message = response
            agent_index = (agent_index + 1) % len(AGENTS)
            turn += 1

            # Delay for readability
            time.sleep(DELAY_BETWEEN_MESSAGES)

        except KeyboardInterrupt:
            print(f"\n")
            print_separator()
            print(f"Logic session ended after {turn} messages")
            print_separator()
            print()
            break
    
    # Handle max turns reached
    if turn >= max_turns:
        print(f"\n")
        print_separator()
        print(f"Logic session completed after {max_turns} messages. Check for emergent logical notation.")
        print_separator()
        print()


def main() -> None:
    """Main function."""
    print_welcome()

    try:
        run_conversation()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\n[Error] {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
