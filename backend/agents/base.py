"""
Base Agent class and shared data models for GG2026 AI agents.
All agents inherit from BaseAgent and share job tracking via MongoDB.
"""
import uuid
import logging
import json
import re
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("agents")


class AgentJob(BaseModel):
    """Tracks an agent task execution."""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: str = ""
    action: str = ""
    params: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # pending | running | completed | failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None


class AgentResult(BaseModel):
    """Standard agent response."""
    success: bool = True
    agent: str = ""
    action: str = ""
    job_id: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class BaseAgent:
    """Base class for all GG2026 AI agents."""

    AGENT_NAME = "base"

    def __init__(self, db: AsyncIOMotorDatabase, llm_key: str = ""):
        self.db = db
        self.llm_key = llm_key

    async def _create_job(self, action: str, params: Dict[str, Any]) -> AgentJob:
        job = AgentJob(agent=self.AGENT_NAME, action=action, params=params, status="running")
        await self.db.agent_jobs.insert_one(
            {k: v for k, v in job.model_dump().items() if k != "_id"}
        )
        return job

    async def _complete_job(self, job: AgentJob, result: Dict[str, Any]):
        now = datetime.now(timezone.utc)
        created = datetime.fromisoformat(job.created_at)
        duration = int((now - created).total_seconds() * 1000)
        await self.db.agent_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": {
                "status": "completed",
                "result": result,
                "completed_at": now.isoformat(),
                "duration_ms": duration,
            }}
        )

    async def _fail_job(self, job: AgentJob, error: str):
        await self.db.agent_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": {
                "status": "failed",
                "error": error,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }}
        )

    async def _ai_generate(self, prompt: str, system_message: str = "Sen profesyonel bir Turkce SEO uzmanisin.") -> str:
        """Call LLM via Emergent integrations."""
        if not self.llm_key:
            raise ValueError("LLM key not configured")
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=self.llm_key,
            session_id=str(uuid.uuid4()),
            system_message=system_message,
        ).with_model("openai", "gpt-4o-mini")
        return await chat.send_message(UserMessage(text=prompt))

    async def _ai_json(self, prompt: str, system_message: str = "Sen bir JSON uretici AI'sin. Sadece gecerli JSON dondur.") -> Dict[str, Any]:
        """Call LLM and parse JSON from response."""
        raw = await self._ai_generate(prompt, system_message)
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group(0))
        match = re.search(r"\[[\s\S]*\]", raw)
        if match:
            return {"items": json.loads(match.group(0))}
        return json.loads(raw)

    def _ok(self, action: str, job_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return AgentResult(
            success=True, agent=self.AGENT_NAME, action=action,
            job_id=job_id, data=data
        ).model_dump()

    def _err(self, action: str, job_id: str, error: str) -> Dict[str, Any]:
        return AgentResult(
            success=False, agent=self.AGENT_NAME, action=action,
            job_id=job_id, error=error
        ).model_dump()
