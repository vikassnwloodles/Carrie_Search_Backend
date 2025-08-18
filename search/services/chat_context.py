from search.models import SearchQuery
import tiktoken


# CONTEXT_LIMIT = 128_000
CONTEXT_LIMIT = 8_000
RESERVED_OUTPUT = int(CONTEXT_LIMIT * 0.20)  # 20% of context limit
SAFETY_BUFFER = int(CONTEXT_LIMIT * 0.01)    # 1% of context limit
MAX_INPUT_TOKENS = CONTEXT_LIMIT - RESERVED_OUTPUT - SAFETY_BUFFER

def build_chat_context(user, current_input_prompt, search_result_id):
    current_input_tokens = count_tokens(current_input_prompt)
    total_tokens = current_input_tokens
    history = []

    # Fetch chat history newest to oldest
    if search_result_id != "null":
        msgs = SearchQuery.objects.filter(user=user, id__lt=search_result_id).order_by('-id')
    else:
        msgs = SearchQuery.objects.filter(user=user).order_by('-id')
        # msgs = SearchQuery.objects.filter(user=user).order_by('-created_at')

    for msg in msgs:
        if total_tokens + msg.response["usage"]["total_tokens"] > MAX_INPUT_TOKENS:
            break

        history.insert(0, {"user": msg.prompt, "assistant": msg.response["choices"][0]["message"]["content"]})  # prepend to maintain chronological order
        total_tokens += msg.response["usage"]["total_tokens"]

    chat_context = []
    for turn in history:
        chat_context.extend([{"role": "user", "content": turn["user"]}, {"role": "assistant", "content": turn["assistant"]}])  

    return chat_context


encoding = tiktoken.encoding_for_model("gpt-4o")
def count_tokens(text):
    return len(encoding.encode(text))