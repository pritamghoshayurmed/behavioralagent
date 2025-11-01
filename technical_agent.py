from dotenv import load_dotenv
from prompts import (
    TECHNICAL_INTERVIEW_INSTRUCTION, 
    BEHAVIORAL_INTERVIEW_INSTRUCTION,
    CAREER_ADVISOR_INSTRUCTION,
    TECHNICAL_SESSION_INSTRUCTION,
    BEHAVIORAL_SESSION_INSTRUCTION,
    CAREER_SESSION_INSTRUCTION
)
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,speechify,deepgram,
    noise_cancellation,
)
# from mcp_client import MCPServerSse
# from mcp_client.agent_tools import MCPToolsIntegration
import os
from tools import open_url, get_career_resources
import sys

load_dotenv()

# Get the agent type from command line argument
AGENT_TYPE = "technical"  # default to technical

# Map agent types to their instructions
AGENT_INSTRUCTIONS = {
    "technical": TECHNICAL_INTERVIEW_INSTRUCTION,
    "behavioral": BEHAVIORAL_INTERVIEW_INSTRUCTION,
    "career": CAREER_ADVISOR_INSTRUCTION
}

SESSION_INSTRUCTIONS = {
    "technical": TECHNICAL_SESSION_INSTRUCTION,
    "behavioral": BEHAVIORAL_SESSION_INSTRUCTION,
    "career": CAREER_SESSION_INSTRUCTION
}


class Assistant(Agent):
    def __init__(self, agent_type: str = "technical") -> None:
        instruction = AGENT_INSTRUCTIONS.get(agent_type, TECHNICAL_INTERVIEW_INSTRUCTION)
        super().__init__(
            instructions=instruction,
            tools=[open_url, get_career_resources],
        )


async def entrypoint(ctx: agents.JobContext):
    import httpx
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3",language="multi"),
        llm=google.LLM(),
        tts=speechify.TTS(model="simba-multilingual"),
    )



    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant(AGENT_TYPE),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Fetch interview context if available (for technical interviews)
    context_summary = ""
    if AGENT_TYPE == "technical":
        try:
            # Try to get session_id from room metadata or name
            room_name = ctx.room.name
            print(f"[AGENT] Room name: {room_name}")
            
            # Extract session_id if it's in the room name (format: session_<session_id>)
            session_id = None
            if "session_" in room_name:
                session_id = room_name.split("session_")[1].split("_")[0]
            elif len(room_name) > 10:  # Assume it might be the session ID itself
                session_id = room_name
            
            if session_id:
                # Fetch context from API
                api_url = os.getenv("INTERVIEW_API_URL", "http://localhost:8000")
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{api_url}/api/interview/context/{session_id}?round_number=2")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success") and data.get("data", {}).get("summary"):
                            context_summary = data["data"]["summary"]
                            print(f"[AGENT] Loaded context: {len(context_summary)} chars")
        except Exception as e:
            print(f"[AGENT] Could not load context: {str(e)}")
            # Continue anyway with default greeting

    # Generate initial reply based on agent type with context
    session_instruction = SESSION_INSTRUCTIONS.get(AGENT_TYPE, TECHNICAL_SESSION_INSTRUCTION)
    
    # Add context to instruction if available
    if context_summary:
        session_instruction = f"""{session_instruction}

CANDIDATE'S PREVIOUS WORK:
{context_summary}

Use this information to ask specific, contextual questions about their implementation.
Reference their code, algorithms, and approach in your questions.
"""
    
    await session.generate_reply(
        instructions=session_instruction,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
