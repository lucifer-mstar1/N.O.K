import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.translation import gettext as _

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _system_prompt(lang: str) -> str:
    # “Psychological” part: supportive + structured + motivating, but not cheesy.
    if lang == "ru":
        return (
            "Ты — AI-учитель N.O.K. Объясняй просто и по шагам, как хороший наставник. "
            "Сначала коротко дай суть, потом пример, затем 2–3 вопроса для проверки. "
            "Если ученик ошибается — мягко исправь и покажи как думать. "
            "Если запрос о домашке — помогай понять, не делай вместо ученика."
        )
    if lang == "uz":
        return (
            "Siz — N.O.K AI-o‘qituvchisiz. Oddiy va bosqichma-bosqich tushuntiring. "
            "Avval qisqa xulosa, keyin misol, so‘ng 2–3 ta tekshiruv savoli bering. "
            "Xatoni muloyim tuzating va fikrlash yo‘lini ko‘rsating. "
            "Uy vazifasida — yechimni tayyorlab bermay, tushunishga yordam bering."
        )
    return (
        "You are N.O.K AI Teacher. Explain clearly and step-by-step like a great mentor. "
        "Start with a short summary, then an example, then 2–3 quick check questions. "
        "Correct mistakes kindly and show the reasoning. "
        "For homework, help the student understand instead of just giving the final answer."
    )


@login_required
@require_http_methods(["GET", "POST"])
def ai_teacher_chat(request):
    answer = ""
    error = ""
    question = ""
    lang = (getattr(request, "LANGUAGE_CODE", "") or "en")[:2]
    if lang not in ("en", "ru", "uz"):
        lang = "en"

    # Conversation memory (last 10 messages) stored per user session
    history = request.session.get("ai_teacher_history", [])
    if not isinstance(history, list):
        history = []

    if request.method == "POST":
        question = (request.POST.get("question") or "").strip()
        if question:
            history.append({"role": "user", "content": question})

            # Keep last 10 messages
            history = history[-10:]

            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key or OpenAI is None:
                error = _("AI teacher is not configured yet. Add OPENAI_API_KEY to your environment.")
            else:
                client = OpenAI(api_key=api_key)
                try:
                    messages = [{"role": "system", "content": _system_prompt(lang)}] + history
                    resp = client.chat.completions.create(
                        model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
                        messages=messages,
                        temperature=0.35,
                    )
                    answer = (resp.choices[0].message.content or "").strip()
                    history.append({"role": "assistant", "content": answer})
                    history = history[-10:]
                except Exception as e:
                    error = str(e)

            request.session["ai_teacher_history"] = history
        else:
            error = _("Please write a question.")

    return render(
        request,
        "aitutor/chat.html",
        {"answer": answer, "question": question, "error": error, "lang": lang, "history": history},
    )
