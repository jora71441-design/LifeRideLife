import ast
import os
import json
import html
import base64
import urllib.request
import urllib.error

ADMIN_ID = 303365656
GITHUB_OWNER = "jora71441-design"
GITHUB_REPO = "LifeRideLife"

# Файлы, которые автоматически складываются в папку js/
JS_FOLDER_FILES = {
    "app.js",
    "quiz.js",
    "calculator.js",
    "winspace.js",
    "upgrade_kits.js",
}


def resolve_repo_path(filename: str, caption: str | None) -> str:
    """Определяет итоговый путь файла в репозитории."""
    if caption and caption.strip():
        clean_caption = caption.strip().lstrip("/")
        if "." in clean_caption:
            return clean_caption
        return f"{clean_caption.rstrip('/')}/{filename}"

    if filename in JS_FOLDER_FILES:
        return f"js/{filename}"

    return filename


def commit_file_to_github(file_bytes: bytes, repo_path: str) -> tuple[bool, str]:
    """Проверяет синтаксис и сохраняет файл в GitHub через REST API."""
    # Предохранитель для Python-файлов
    if repo_path.endswith(".py"):
        try:
            source_code = file_bytes.decode("utf-8")
            ast.parse(source_code)
        except SyntaxError as e:
            return False, f"⛔️ <b>Синтаксическая ошибка в Python</b> (строка {e.lineno}):\n<code>{html.escape(str(e.msg))}</code>\nЗагрузка отменена."
        except UnicodeDecodeError:
            return False, "⛔️ Ошибка кодировки файла (ожидается UTF-8)."

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        return False, "⚠️ Не задана переменная <code>GITHUB_TOKEN</code> в настройках Render."

    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "LifeRideLife-Bot-Uploader",
    }

    # 1. Получаем текущий SHA файла, если он уже существует
    sha = None
    try:
        req_get = urllib.request.Request(api_url, headers=headers, method="GET")
        with urllib.request.urlopen(req_get, timeout=15) as resp:
            existing_data = json.loads(resp.read().decode("utf-8"))
            sha = existing_data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return False, f"Ошибка чтения GitHub ({e.code}): {html.escape(str(e.reason))}"
    except Exception as e:
        return False, f"Ошибка сети при проверке файла: {html.escape(str(e))}"

    # 2. Отправляем коммит на обновление/создание
    payload = {
        "message": f"bot-deploy: update {repo_path}",
        "content": base64.b64encode(file_bytes).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req_put = urllib.request.Request(
            api_url, data=data_bytes, headers=headers, method="PUT"
        )
        with urllib.request.urlopen(req_put, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            commit_url = result.get("commit", {}).get("html_url", "")
            action = "обновлён" if sha else "создан"
            return True, f"✅ Файл <code>{repo_path}</code> успешно {action}!\n🔗 <a href=\"{commit_url}\">Посмотреть коммит на GitHub</a>"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return False, f"Ошибка записи GitHub ({e.code}):\n<code>{html.escape(err_body[:200])}</code>"
    except Exception as e:
        return False, f"Ошибка при отправке коммита: {html.escape(str(e))}"
