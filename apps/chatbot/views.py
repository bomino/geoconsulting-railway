import json
import logging

from django.http import JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit

from apps.chatbot.prompt import build_system_prompt
from apps.chatbot.services import (
    get_openai_client,
    is_circuit_open,
    record_failure,
    record_success,
)

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_ENTRIES = 50


@method_decorator(ratelimit(key="ip", rate="20/5m", method="POST", block=True), name="dispatch")
class ChatbotView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Corps de requete invalide."}, status=400)

        user_message = body.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Le message est requis."}, status=400)

        if len(user_message) > MAX_MESSAGE_LENGTH:
            return JsonResponse(
                {"error": f"Le message ne doit pas depasser {MAX_MESSAGE_LENGTH} caracteres."},
                status=400,
            )

        history = body.get("history", [])
        if not isinstance(history, list):
            history = []
        history = history[:MAX_HISTORY_ENTRIES]

        if is_circuit_open():
            return JsonResponse(
                {"error": "Le service est temporairement indisponible. Veuillez reessayer dans quelques minutes."},
                status=503,
            )

        system_prompt = build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        for entry in history:
            role = entry.get("role")
            content = entry.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content[:MAX_MESSAGE_LENGTH]})

        messages.append({"role": "user", "content": user_message})

        try:
            client = get_openai_client()
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                max_tokens=1024,
                temperature=0.7,
            )
            record_success()

            def event_stream():
                try:
                    for chunk in stream:
                        delta = chunk.choices[0].delta if chunk.choices else None
                        if delta and delta.content:
                            yield f"data: {json.dumps({'content': delta.content})}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception:
                    logger.exception("Streaming error")
                    record_failure()
                    yield f"data: {json.dumps({'error': 'Erreur pendant le streaming.'})}\n\n"

            return StreamingHttpResponse(
                event_stream(),
                content_type="text/event-stream",
            )

        except Exception:
            logger.exception("OpenAI API error")
            record_failure()
            return JsonResponse(
                {"error": "Erreur de communication avec le service IA."},
                status=502,
            )
