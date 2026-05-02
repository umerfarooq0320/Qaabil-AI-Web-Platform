"""
Async MongoDB connection using Motor.
Used for behavior logs, voice sessions, and state snapshots.
(MOCKED for local development to avoid MongoDB dependency)
"""

import logging

logger = logging.getLogger(__name__)

class MockCollection:
    async def insert_one(self, data):
        logger.debug(f"Mock MongoDB insert: {data}")
        return None

_mock_collection = MockCollection()

def behavior_logs_collection():
    return _mock_collection

def voice_sessions_collection():
    return _mock_collection

def user_state_snapshots_collection():
    return _mock_collection

async def close_mongo():
    pass
