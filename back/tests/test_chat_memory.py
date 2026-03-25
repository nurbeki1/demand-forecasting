"""
Test cases for Chat Memory
"""
import pytest
import time
from datetime import datetime, timedelta
from memory.chat_memory import ChatMemory, ChatMessage, chat_memory


class TestChatMemoryBasic:
    """Basic tests for ChatMemory"""

    def setup_method(self):
        """Create fresh memory instance for each test"""
        self.memory = ChatMemory(max_messages=5, ttl_hours=1, context_window=3)

    def test_add_message(self):
        """Should add message successfully"""
        msg = self.memory.add_message(1, "user", "Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)

    def test_add_message_with_data(self):
        """Should add message with additional data"""
        data = {"chart": [1, 2, 3]}
        msg = self.memory.add_message(1, "assistant", "Response", data=data)
        assert msg.data == data

    def test_add_message_with_intent(self):
        """Should add message with intent"""
        msg = self.memory.add_message(1, "user", "Forecast", intent="forecast")
        assert msg.intent == "forecast"

    def test_get_history_empty(self):
        """Should return empty list for new user"""
        history = self.memory.get_history(999)
        assert history == []

    def test_get_history_after_add(self):
        """Should return messages after adding"""
        self.memory.add_message(1, "user", "Hello")
        self.memory.add_message(1, "assistant", "Hi there")

        history = self.memory.get_history(1)
        assert len(history) == 2
        assert history[0]["content"] == "Hello"
        assert history[1]["content"] == "Hi there"


class TestChatMemoryUserIsolation:
    """Tests for user isolation"""

    def setup_method(self):
        self.memory = ChatMemory()

    def test_users_have_separate_histories(self):
        """Different users should have separate histories"""
        self.memory.add_message(1, "user", "User 1 message")
        self.memory.add_message(2, "user", "User 2 message")

        history1 = self.memory.get_history(1)
        history2 = self.memory.get_history(2)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "User 1 message"
        assert history2[0]["content"] == "User 2 message"

    def test_clear_only_affects_user(self):
        """Clearing history should only affect specific user"""
        self.memory.add_message(1, "user", "User 1")
        self.memory.add_message(2, "user", "User 2")

        self.memory.clear_history(1)

        assert len(self.memory.get_history(1)) == 0
        assert len(self.memory.get_history(2)) == 1


class TestChatMemoryLimits:
    """Tests for message limits"""

    def test_respects_max_messages(self):
        """Should trim to max_messages"""
        memory = ChatMemory(max_messages=3)

        for i in range(5):
            memory.add_message(1, "user", f"Message {i}")

        history = memory.get_history(1)
        assert len(history) == 3
        # Should keep the last 3
        assert history[0]["content"] == "Message 2"
        assert history[2]["content"] == "Message 4"

    def test_get_history_with_limit(self):
        """Should respect limit parameter"""
        memory = ChatMemory(max_messages=10)

        for i in range(5):
            memory.add_message(1, "user", f"Message {i}")

        history = memory.get_history(1, limit=2)
        assert len(history) == 2
        # Should get the last 2
        assert history[0]["content"] == "Message 3"
        assert history[1]["content"] == "Message 4"


class TestChatMemoryContextWindow:
    """Tests for context window"""

    def setup_method(self):
        self.memory = ChatMemory(max_messages=10, context_window=3)

    def test_context_window_format(self):
        """Should format context window correctly"""
        self.memory.add_message(1, "user", "Question 1")
        self.memory.add_message(1, "assistant", "Answer 1")
        self.memory.add_message(1, "user", "Question 2")

        context = self.memory.get_context_window(1)

        assert "User: Question 1" in context
        assert "Assistant: Answer 1" in context
        assert "User: Question 2" in context

    def test_context_window_respects_limit(self):
        """Should only include context_window messages"""
        for i in range(10):
            self.memory.add_message(1, "user", f"Message {i}")

        context = self.memory.get_context_window(1)

        # Should only have last 3 messages
        assert "Message 7" in context
        assert "Message 8" in context
        assert "Message 9" in context
        assert "Message 0" not in context

    def test_empty_context_window(self):
        """Should handle empty history"""
        context = self.memory.get_context_window(999)
        assert context == "No previous conversation."


class TestChatMemoryLLMMessages:
    """Tests for LLM message formatting"""

    def setup_method(self):
        self.memory = ChatMemory(context_window=5)

    def test_llm_messages_format(self):
        """Should format messages for OpenAI API"""
        self.memory.add_message(1, "user", "Hello")
        self.memory.add_message(1, "assistant", "Hi")

        messages = self.memory.get_llm_messages(1, "System prompt here")

        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt here"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_llm_messages_empty_history(self):
        """Should work with empty history"""
        messages = self.memory.get_llm_messages(999, "System prompt")

        assert len(messages) == 1
        assert messages[0]["role"] == "system"


class TestChatMemoryClear:
    """Tests for clearing history"""

    def setup_method(self):
        self.memory = ChatMemory()

    def test_clear_returns_count(self):
        """Should return count of cleared messages"""
        self.memory.add_message(1, "user", "M1")
        self.memory.add_message(1, "user", "M2")
        self.memory.add_message(1, "user", "M3")

        count = self.memory.clear_history(1)
        assert count == 3

    def test_clear_nonexistent_user(self):
        """Should return 0 for nonexistent user"""
        count = self.memory.clear_history(999)
        assert count == 0

    def test_history_empty_after_clear(self):
        """History should be empty after clear"""
        self.memory.add_message(1, "user", "Message")
        self.memory.clear_history(1)

        assert len(self.memory.get_history(1)) == 0


class TestChatMemorySessionInfo:
    """Tests for session info"""

    def setup_method(self):
        self.memory = ChatMemory(ttl_hours=1)

    def test_session_info_new_user(self):
        """Should return not exists for new user"""
        info = self.memory.get_session_info(999)
        assert info["exists"] == False
        assert info["message_count"] == 0

    def test_session_info_existing_user(self):
        """Should return session info for existing user"""
        self.memory.add_message(1, "user", "Hello")
        self.memory.add_message(1, "assistant", "Hi")

        info = self.memory.get_session_info(1)

        assert info["exists"] == True
        assert info["user_id"] == 1
        assert info["message_count"] == 2
        assert "created_at" in info
        assert "last_activity" in info
        assert "ttl_remaining_hours" in info

    def test_all_sessions_info(self):
        """Should return info for all sessions"""
        self.memory.add_message(1, "user", "User 1")
        self.memory.add_message(2, "user", "User 2")

        info = self.memory.get_all_sessions_info()

        assert info["total_sessions"] == 2
        assert info["total_messages"] == 2
        assert len(info["sessions"]) == 2


class TestChatMemoryHistoryFormat:
    """Tests for history message format"""

    def setup_method(self):
        self.memory = ChatMemory()

    def test_history_message_fields(self):
        """History messages should have all fields"""
        self.memory.add_message(
            1, "user", "Test",
            data={"key": "value"},
            intent="test_intent"
        )

        history = self.memory.get_history(1)
        msg = history[0]

        assert "role" in msg
        assert "content" in msg
        assert "timestamp" in msg
        assert "data" in msg
        assert "intent" in msg

        assert msg["role"] == "user"
        assert msg["content"] == "Test"
        assert msg["data"] == {"key": "value"}
        assert msg["intent"] == "test_intent"

    def test_timestamp_is_iso_format(self):
        """Timestamp should be ISO format string"""
        self.memory.add_message(1, "user", "Test")

        history = self.memory.get_history(1)
        timestamp = history[0]["timestamp"]

        # Should be parseable as ISO format
        datetime.fromisoformat(timestamp)


class TestChatMemoryGlobal:
    """Tests for global chat_memory instance"""

    def test_global_instance_exists(self):
        """Global instance should exist"""
        assert chat_memory is not None

    def test_global_instance_is_chatmemory(self):
        """Global instance should be ChatMemory"""
        assert isinstance(chat_memory, ChatMemory)

    def test_global_instance_has_defaults(self):
        """Global instance should have default settings"""
        assert chat_memory.max_messages == 20
        assert chat_memory.context_window == 10


class TestChatMemoryThreadSafety:
    """Tests for thread safety"""

    def test_concurrent_adds(self):
        """Should handle concurrent adds"""
        import threading

        memory = ChatMemory()
        results = []

        def add_messages(user_id, count):
            for i in range(count):
                memory.add_message(user_id, "user", f"Message {i}")
            results.append(len(memory.get_history(user_id)))

        threads = [
            threading.Thread(target=add_messages, args=(i, 10))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each user should have 10 messages
        for i in range(5):
            assert len(memory.get_history(i)) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
