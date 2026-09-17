import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import Conversation, Message
from .services import get_generator


@login_required
def conversation_view(request):
    return render(request, "chat/conversation.html")


def _get_recent_messages(conversation, limit=None):
    limit = limit or getattr(settings, 'M2_CONTEXT_MESSAGE_LIMIT', 8)
    messages = list(
        conversation.messages.order_by('-created_at').values('role', 'content')[:limit]
    )
    return [
        {"role": item["role"], "content": item["content"]}
        for item in reversed(messages)
    ]


@login_required
@require_http_methods(["POST"])
def message_view(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    content = payload.get("message", "")
    if not isinstance(content, str) or not content.strip():
        return JsonResponse({"error": "Message cannot be empty."}, status=400)

    conversation_id = payload.get("conversation_id")
    if conversation_id:
        conversation = Conversation.objects.filter(
            id=conversation_id,
            user=request.user,
        ).first()
        if conversation is None:
            return JsonResponse({"error": "Conversation not found."}, status=404)
    else:
        conversation = Conversation.objects.create(user=request.user)

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=content.strip(),
    )

    recent_messages = _get_recent_messages(conversation)
    response = get_generator().generate(messages=recent_messages, context=content.strip())

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=response.text,
    )

    return JsonResponse(
        {
            "conversation_id": conversation.id,
            "response": response.text,
            "model": response.model_name,
            "backend": response.backend,
            "sources": response.sources or [],
        }
    )
