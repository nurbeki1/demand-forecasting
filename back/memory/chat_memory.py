"""
Chat Memory with user isolation, message limits, and TTL
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import threading


@dataclass
class ChatMessage:
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None  # Additional data (charts, stats, etc.)
    intent: Optional[str] = None


@dataclass
class EntityContext:
    """Tracked entities across conversation"""
    products: List[str] = field(default_factory=list)  # Product IDs/names mentioned
    categories: List[str] = field(default_factory=list)  # Categories discussed
    regions: List[str] = field(default_factory=list)  # Regions mentioned
    last_product: Optional[str] = None  # Most recent product (for "it", "this")
    last_intent: Optional[str] = None  # Last classified intent
    preferences: Dict[str, Any] = field(default_factory=dict)  # User preferences


@dataclass
class UserSession:
    """User chat session"""
    user_id: int
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    entity_context: EntityContext = field(default_factory=EntityContext)


class ChatMemory:
    """
    Thread-safe chat memory with user isolation, limits, and TTL
    """

    def __init__(
        self,
        max_messages: int = 20,
        ttl_hours: int = 24,
        context_window: int = 10
    ):
        self.max_messages = max_messages
        self.ttl = timedelta(hours=ttl_hours)
        self.context_window = context_window
        self._sessions: Dict[int, UserSession] = {}
        self._lock = threading.RLock()

    def _get_session(self, user_id: int) -> UserSession:
        """Get or create user session"""
        with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = UserSession(user_id=user_id)
            return self._sessions[user_id]

    def _cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.now()
        with self._lock:
            expired = [
                uid for uid, session in self._sessions.items()
                if now - session.last_activity > self.ttl
            ]
            for uid in expired:
                del self._sessions[uid]

    def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> ChatMessage:
        """
        Add a message to user's chat history

        Args:
            user_id: User ID
            role: "user" or "assistant"
            content: Message content
            data: Optional additional data
            intent: Optional classified intent

        Returns:
            The created ChatMessage
        """
        message = ChatMessage(
            role=role,
            content=content,
            data=data,
            intent=intent
        )

        with self._lock:
            session = self._get_session(user_id)
            session.messages.append(message)
            session.last_activity = datetime.now()

            # Trim to max messages
            if len(session.messages) > self.max_messages:
                session.messages = session.messages[-self.max_messages:]

        # Periodic cleanup
        self._cleanup_expired()

        return message

    def get_history(
        self,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's chat history

        Args:
            user_id: User ID
            limit: Optional limit on number of messages

        Returns:
            List of message dictionaries
        """
        with self._lock:
            session = self._get_session(user_id)
            messages = session.messages

            if limit:
                messages = messages[-limit:]

            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "data": msg.data,
                    "intent": msg.intent,
                }
                for msg in messages
            ]

    def get_context_window(self, user_id: int) -> str:
        """
        Get formatted context window for LLM

        Args:
            user_id: User ID

        Returns:
            Formatted string of recent conversation
        """
        history = self.get_history(user_id, limit=self.context_window)

        if not history:
            return "No previous conversation."

        lines = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")

        return "\n".join(lines)

    def get_last_messages(
        self,
        user_id: int,
        n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get last N messages for user

        Args:
            user_id: User ID
            n: Number of messages

        Returns:
            List of message dictionaries
        """
        return self.get_history(user_id, limit=n)

    def get_llm_messages(
        self,
        user_id: int,
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """
        Get messages formatted for OpenAI API

        Args:
            user_id: User ID
            system_prompt: System prompt to include

        Returns:
            List of message dicts for OpenAI API
        """
        messages = [{"role": "system", "content": system_prompt}]

        history = self.get_history(user_id, limit=self.context_window)
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        return messages

    def clear_history(self, user_id: int) -> int:
        """
        Clear user's chat history

        Args:
            user_id: User ID

        Returns:
            Number of messages cleared
        """
        with self._lock:
            if user_id in self._sessions:
                count = len(self._sessions[user_id].messages)
                self._sessions[user_id].messages = []
                return count
            return 0

    def track_entities(
        self,
        user_id: int,
        product_ids: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        category: Optional[str] = None,
        region: Optional[str] = None,
        intent: Optional[str] = None
    ) -> None:
        """
        Track entities mentioned in conversation

        Args:
            user_id: User ID
            product_ids: List of product IDs mentioned
            search_query: Search query (product name)
            category: Category mentioned
            region: Region mentioned
            intent: Classified intent
        """
        with self._lock:
            session = self._get_session(user_id)
            ctx = session.entity_context

            # Track products (keep last 10)
            if product_ids:
                for pid in product_ids:
                    if pid not in ctx.products:
                        ctx.products.append(pid)
                ctx.products = ctx.products[-10:]
                ctx.last_product = product_ids[-1]

            # Track search queries as product references
            if search_query:
                if search_query not in ctx.products:
                    ctx.products.append(search_query)
                ctx.products = ctx.products[-10:]
                ctx.last_product = search_query

            # Track categories (keep last 5)
            if category and category not in ctx.categories:
                ctx.categories.append(category)
                ctx.categories = ctx.categories[-5:]

            # Track regions (keep last 4)
            if region and region not in ctx.regions:
                ctx.regions.append(region)
                ctx.regions = ctx.regions[-4:]

            # Track last intent
            if intent:
                ctx.last_intent = intent

    def get_entity_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get tracked entity context for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with entity context
        """
        with self._lock:
            session = self._get_session(user_id)
            ctx = session.entity_context

            return {
                "products": ctx.products,
                "last_product": ctx.last_product,
                "categories": ctx.categories,
                "regions": ctx.regions,
                "last_intent": ctx.last_intent,
                "preferences": ctx.preferences,
            }

    def get_smart_context_window(self, user_id: int) -> str:
        """
        Get enhanced context window with entity tracking

        Args:
            user_id: User ID

        Returns:
            Formatted string of recent conversation with entity summary
        """
        history = self.get_history(user_id, limit=self.context_window)
        entity_ctx = self.get_entity_context(user_id)

        lines = []

        # Add entity summary
        if entity_ctx["products"]:
            lines.append(f"[Products discussed: {', '.join(entity_ctx['products'][-5:])}]")
        if entity_ctx["last_product"]:
            lines.append(f"[Most recent: {entity_ctx['last_product']}]")
        if entity_ctx["categories"]:
            lines.append(f"[Categories: {', '.join(entity_ctx['categories'])}]")
        if entity_ctx["regions"]:
            lines.append(f"[Regions: {', '.join(entity_ctx['regions'])}]")

        if lines:
            lines.append("")  # Empty line before conversation

        # Add conversation history
        if not history:
            lines.append("No previous conversation.")
        else:
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                # Truncate long messages
                content = msg['content'][:500] + "..." if len(msg['content']) > 500 else msg['content']
                lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def resolve_reference(self, user_id: int, text: str) -> Optional[str]:
        """
        Resolve pronouns like "it", "this product" to actual product

        Args:
            user_id: User ID
            text: User message text

        Returns:
            The resolved product ID/name or None
        """
        # Check for reference words
        reference_words = [
            "it", "this", "that", "this product", "that product",
            "это", "этот", "этот товар", "этот продукт",
            "его", "её", "ей", "о нём", "о ней"
        ]

        text_lower = text.lower()
        has_reference = any(ref in text_lower for ref in reference_words)

        if has_reference:
            with self._lock:
                session = self._get_session(user_id)
                return session.entity_context.last_product

        return None

    def set_preference(self, user_id: int, key: str, value: Any) -> None:
        """
        Set a user preference

        Args:
            user_id: User ID
            key: Preference key
            value: Preference value
        """
        with self._lock:
            session = self._get_session(user_id)
            session.entity_context.preferences[key] = value

    def get_preference(self, user_id: int, key: str, default: Any = None) -> Any:
        """
        Get a user preference

        Args:
            user_id: User ID
            key: Preference key
            default: Default value if not set

        Returns:
            Preference value or default
        """
        with self._lock:
            session = self._get_session(user_id)
            return session.entity_context.preferences.get(key, default)

    def get_session_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get session info for user

        Args:
            user_id: User ID

        Returns:
            Session information dictionary
        """
        with self._lock:
            if user_id not in self._sessions:
                return {
                    "exists": False,
                    "message_count": 0,
                }

            session = self._sessions[user_id]
            return {
                "exists": True,
                "user_id": user_id,
                "message_count": len(session.messages),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "ttl_remaining_hours": max(
                    0,
                    (self.ttl - (datetime.now() - session.last_activity)).total_seconds() / 3600
                ),
            }

    def get_all_sessions_info(self) -> Dict[str, Any]:
        """
        Get info about all active sessions (for admin)

        Returns:
            Dictionary with session statistics
        """
        self._cleanup_expired()

        with self._lock:
            return {
                "total_sessions": len(self._sessions),
                "total_messages": sum(
                    len(s.messages) for s in self._sessions.values()
                ),
                "sessions": [
                    self.get_session_info(uid)
                    for uid in self._sessions.keys()
                ],
            }


# Global chat memory instance
chat_memory = ChatMemory(
    max_messages=20,
    ttl_hours=24,
    context_window=10
)
