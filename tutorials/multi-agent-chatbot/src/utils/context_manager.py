from typing import List, Dict, Any
import re

class ContextManager:
    """Manages context windows and token optimization for the multi-agent system"""
    
    def __init__(self, max_tokens: int = 4096, model: str = "gpt-4"):
        self.max_tokens = max_tokens
        # Simplified token counting without tiktoken for demo
        self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (simplified estimation)"""
        if not text:
            return 0
        # Simple estimation: ~4 characters per token
        return len(str(text)) // 4
    
    def compress_context(self, messages: List[Dict[str, Any]], 
                        preserve_recent: int = 5) -> List[Dict[str, Any]]:
        """Compress conversation history while preserving important context"""
        if len(messages) <= preserve_recent:
            return messages
        
        # Keep system message and recent messages
        compressed = []
        if messages and messages[0].get("role") == "system":
            compressed.append(messages[0])
            recent_start = -preserve_recent
        else:
            recent_start = -preserve_recent
        
        # Summarize middle messages
        middle_messages = messages[len(compressed):recent_start]
        if middle_messages:
            summary = self._summarize_messages(middle_messages)
            compressed.append({
                "role": "system",
                "content": f"Previous conversation summary: {summary}"
            })
        
        # Add recent messages
        compressed.extend(messages[recent_start:])
        return compressed
    
    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize a list of messages"""
        key_points = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                key_points.append(f"User asked: {content[:100]}...")
            elif role == "assistant":
                key_points.append(f"Assistant responded about: {content[:100]}...")
        
        return " ".join(key_points[-5:])  # Keep last 5 key points
    
    def chunk_document(self, document: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split document into semantic chunks"""
        if not document:
            return []
        
        # Simple chunking by sentences
        sentences = re.split(r'[.!?]+', document)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self.count_tokens(potential_chunk) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                current_chunk = sentence
            else:
                current_chunk = potential_chunk
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_context_window(self, 
                            current_task: str,
                            history: List[Dict[str, Any]],
                            relevant_docs: List[str] = None) -> str:
        """Create optimized context window for current task"""
        context_parts = []
        remaining_tokens = self.max_tokens
        
        # Add current task (highest priority)
        task_tokens = self.count_tokens(current_task)
        if task_tokens < remaining_tokens:
            context_parts.append(f"Current Task: {current_task}")
            remaining_tokens -= task_tokens
        
        # Add compressed history
        compressed_history = self.compress_context(history or [])
        history_text = "\n".join([
            f"{m.get('role', 'unknown')}: {m.get('content', '')}" 
            for m in compressed_history
        ])
        history_tokens = self.count_tokens(history_text)
        
        if history_tokens < remaining_tokens:
            context_parts.append(f"Conversation History:\n{history_text}")
            remaining_tokens -= history_tokens
        
        # Add relevant documents
        if relevant_docs:
            for doc in relevant_docs:
                doc_tokens = self.count_tokens(doc)
                if doc_tokens < remaining_tokens:
                    context_parts.append(f"Relevant Information:\n{doc}")
                    remaining_tokens -= doc_tokens
                else:
                    # Truncate if needed
                    truncated = self._truncate_to_tokens(doc, remaining_tokens - 100)
                    context_parts.append(f"Relevant Information (truncated):\n{truncated}")
                    break
        
        return "\n\n---\n\n".join(context_parts)
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        if not text:
            return ""
        
        # Simple character-based truncation
        estimated_chars = max_tokens * 4
        if len(text) <= estimated_chars:
            return text
        
        return text[:estimated_chars] + "..."
    
    def _get_recent_context(self, state: Dict[str, Any], max_messages: int = 5) -> str:
        """Get recent conversation context from state"""
        messages = state.get("messages", [])
        recent_messages = messages[-max_messages:]
        context = []
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context.append(f"{role}: {content[:200]}...")
        return "\n".join(context)