from search.models import SearchQuery
import tiktoken


CONTEXT_LIMIT = 128_000
RESERVED_OUTPUT = int(CONTEXT_LIMIT * 0.20)  # 20% of context limit
SAFETY_BUFFER = int(CONTEXT_LIMIT * 0.01)    # 1% of context limit
MAX_INPUT_TOKENS = CONTEXT_LIMIT - RESERVED_OUTPUT - SAFETY_BUFFER

def build_chat_context(user, current_input_prompt):
    current_input_tokens = count_tokens(current_input_prompt)
    total_tokens = current_input_tokens
    history = []

    # Fetch chat history newest to oldest
    for msg in SearchQuery.objects.filter(user=user).order_by('-created_at'):
        if total_tokens + msg.response["usage"]["total_tokens"] > MAX_INPUT_TOKENS:
            break
        # history.insert(0, msg.response["choices"][0]["message"]["content"])  # prepend to maintain chronological order
        history.insert(0, {"User": msg.prompt, "Assistant": msg.response["choices"][0]["message"]["content"]})  # prepend to maintain chronological order
        total_tokens += msg.response["usage"]["total_tokens"]

    parts = [f"User: {turn['User']}\nAssistant: {turn['Assistant']}" for turn in history]
    parts.append(f"User: {current_input_prompt}\nAssistant: ")
    final_prompt = "\n".join(parts)

    return final_prompt


encoding = tiktoken.encoding_for_model("gpt-4o")
def count_tokens(text):
    return len(encoding.encode(text))