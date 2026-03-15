"""
Telegram Bot Manager
- Automated bot creation via Telethon (BotFather)
- Webhook-based bot runner via Telegram Bot API
- Subscriber tracking & broadcast messaging
"""

import asyncio
import re
import os
import logging
import httpx
from typing import Optional
from pathlib import Path

logger = logging.getLogger("telegram_bot_manager")

TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"
SESSION_PATH = str(Path(__file__).parent / "telegram_session")


def firm_name_to_bot_username(name: str) -> str:
    """Convert firm name to Telegram bot username.
    Rules: a-z, 0-9, underscore only. Must start with letter. Ends with _bot.
    Example: MAXWIN -> maxwin_guncel2026_bot
    """
    clean = name.lower().strip()
    clean = re.sub(r'[^a-z0-9]', '', clean)
    if not clean:
        clean = "firma"
    # Telegram usernames must start with a letter
    if clean[0].isdigit():
        clean = "x" + clean
    username = f"{clean}_guncel2026_bot"
    # Ensure length <= 32
    if len(username) > 32:
        max_name_len = 32 - len("_guncel2026_bot")
        clean = clean[:max_name_len]
        username = f"{clean}_guncel2026_bot"
    return username


async def telegram_api_call(token: str, method: str, data: dict = None) -> dict:
    """Make a Telegram Bot API call."""
    url = f"{TELEGRAM_API_BASE.format(token=token)}/{method}"
    async with httpx.AsyncClient(timeout=30) as client:
        if data:
            resp = await client.post(url, json=data)
        else:
            resp = await client.get(url)
        return resp.json()


async def set_bot_webhook(token: str, webhook_url: str) -> dict:
    """Set webhook for a bot."""
    return await telegram_api_call(token, "setWebhook", {
        "url": webhook_url,
        "allowed_updates": ["message"],
        "drop_pending_updates": True,
    })


async def delete_bot_webhook(token: str) -> dict:
    """Remove webhook for a bot."""
    return await telegram_api_call(token, "deleteWebhook", {"drop_pending_updates": True})


async def get_bot_info(token: str) -> dict:
    """Get bot info via getMe."""
    return await telegram_api_call(token, "getMe")


async def send_telegram_message(token: str, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None) -> dict:
    """Send a message via bot."""
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return await telegram_api_call(token, "sendMessage", data)


async def set_bot_commands(token: str) -> dict:
    """Set command list for bot."""
    commands = [
        {"command": "start", "description": "Hoşgeldin mesajı ve güncel giriş"},
        {"command": "bonus", "description": "Aktif bonus ve promosyonlar"},
        {"command": "link", "description": "Güncel giriş linki"},
        {"command": "destek", "description": "Destek ve iletişim bilgileri"},
    ]
    return await telegram_api_call(token, "setMyCommands", {"commands": commands})


async def set_bot_profile(token: str, firm: dict) -> None:
    """Set bot profile: description, short description, name."""
    name = firm.get("name", "Firma")
    bonus = firm.get("bonus_amount", "")
    bonus_type = firm.get("bonus_type", "")
    rating = firm.get("rating", "")
    features = firm.get("features", [])

    # Bot display name (max 64 chars)
    display_name = f"{name} Güncel Giriş 2026"
    if len(display_name) > 64:
        display_name = display_name[:64]
    await telegram_api_call(token, "setMyName", {"name": display_name})

    # Short description (max 120 chars) - shown in bot search/sharing
    short_desc = f"{name} | Güncel giriş adresi, bonus ve promosyon bilgileri"
    if bonus:
        short_desc += f" | {bonus}"
    if len(short_desc) > 120:
        short_desc = short_desc[:120]
    await telegram_api_call(token, "setMyShortDescription", {"short_description": short_desc})

    # Full description (max 512 chars) - shown on bot profile before /start
    type_labels = {"deneme": "Deneme Bonusu", "hosgeldin": "Hoşgeldin Bonusu", "kayip": "Kayıp Bonusu"}
    desc = f"🔗 {name} — Güncel Giriş Botu 2026\n\n"
    if bonus:
        label = type_labels.get(bonus_type, bonus_type.title()) if bonus_type else ""
        desc += f"🎁 Bonus: {bonus}"
        if label:
            desc += f" ({label})"
        desc += "\n"
    if rating:
        desc += f"⭐ Puan: {rating}/5\n"
    if features:
        desc += f"✅ {', '.join(features)}\n"
    desc += "\n"
    desc += "📌 Bu bot ile yapabilecekleriniz:\n\n"
    desc += "• Güncel giriş adresine anında ulaşın\n"
    desc += "• Aktif bonus ve promosyonları görüntüleyin\n"
    desc += "• Yeni kampanyalardan anında haberdar olun\n"
    desc += "• 7/24 canlı destek bilgisi alın\n\n"
    desc += "🚀 Başlamak için START butonuna basın!\n\n"
    desc += "START'lamak istemezseniz PROMOCODE kazanmak için @PromocodeAI_bot'a yada\n"
    desc += "Güncel Deneme Bonusu Rehberine göz atın!\n"
    desc += "xlinks.art/guncelgirisai"
    if len(desc) > 512:
        desc = desc[:512]
    await telegram_api_call(token, "setMyDescription", {"description": desc})


def build_start_message(firm: dict) -> str:
    """Build /start welcome message for a firm."""
    name = firm.get("name", "Firma")
    bonus = firm.get("bonus_amount", "")
    bonus_type = firm.get("bonus_type", "")
    affiliate = firm.get("affiliate_url", "")
    slug = firm.get("slug", "")
    rating = firm.get("rating", "")
    features = firm.get("features", [])

    msg = f"{'━' * 28}\n"
    msg += f"  <b>{name}</b>\n"
    msg += "  Güncel Giriş Botu 2026\n"
    msg += f"{'━' * 28}\n\n"

    msg += "Hoş geldiniz! Bu bot ile <b>güncel giriş adresi</b>, "
    msg += "<b>bonus bilgileri</b> ve <b>promosyonlara</b> anında ulaşabilirsiniz.\n\n"

    if bonus:
        msg += f"🎁 <b>Hoşgeldin Bonusu:</b> <b>{bonus}</b>"
        if bonus_type:
            type_labels = {"deneme": "Deneme Bonusu", "hosgeldin": "Hoşgeldin Bonusu", "kayip": "Kayıp Bonusu"}
            msg += f" — {type_labels.get(bonus_type, bonus_type.title())}"
        msg += "\n"

    if rating:
        stars = "⭐" * int(float(rating))
        msg += f"📊 <b>Puan:</b> {rating}/5 {stars}\n"

    if features:
        msg += f"✅ <b>Özellikler:</b> {', '.join(features)}\n"

    msg += "\n"
    msg += "📌 <b>Kullanılabilir Komutlar:</b>\n\n"
    msg += "  /bonus  →  Güncel bonus ve promosyonlar\n"
    msg += "  /link   →  Güncel giriş adresi\n"
    msg += "  /destek →  Canlı destek bilgisi\n\n"

    msg += f"{'─' * 28}\n"
    msg += "🔔 Yeni promosyon ve güncellemelerden\n"
    msg += "    haberdar olmak için botu kayıtlı tutun!\n"

    buttons = []
    if affiliate:
        buttons.append([{"text": "🚀 Hemen Giriş Yap", "url": affiliate}])
    if slug:
        buttons.append([{"text": "📖 Site İncelemesi", "url": f"https://guncelgiris.ai/{slug}"}])
    if buttons:
        buttons.append([{"text": "🌐 guncelgiris.ai", "url": "https://guncelgiris.ai"}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    return msg, reply_markup


def build_bonus_message(firm: dict) -> str:
    """Build /bonus message."""
    name = firm.get("name", "Firma")
    bonus = firm.get("bonus_amount", "")
    bonus_type = firm.get("bonus_type", "")
    turnover = firm.get("turnover_requirement", "")
    affiliate = firm.get("affiliate_url", "")

    msg = f"{'━' * 28}\n"
    msg += f"  🎁 {name} — Bonus Bilgileri\n"
    msg += f"{'━' * 28}\n\n"

    if bonus:
        msg += f"💰 <b>Bonus Miktarı:</b> <b>{bonus}</b>\n\n"

    if bonus_type:
        type_labels = {"deneme": "Deneme Bonusu", "hosgeldin": "Hoşgeldin Bonusu", "kayip": "Kayıp Bonusu"}
        label = type_labels.get(bonus_type, bonus_type.title())
        msg += f"📋 <b>Bonus Türü:</b> {label}\n"

    if turnover:
        msg += f"🔄 <b>Çevrim Şartı:</b> {turnover}x\n"

    msg += "\n"
    msg += "📌 <b>Bonus Alma Adımları:</b>\n\n"
    msg += "  1️⃣  Aşağıdaki butona tıklayın\n"
    msg += "  2️⃣  Üye olun veya giriş yapın\n"
    msg += "  3️⃣  Bonus otomatik tanımlanır\n\n"

    msg += f"{'─' * 28}\n"
    msg += "⚡ Bonus fırsatları sınırlı süreli olabilir\n"

    buttons = []
    if affiliate:
        buttons.append([{"text": "🎁 Bonusu Al — Hemen Giriş Yap", "url": affiliate}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    return msg, reply_markup


def build_link_message(firm: dict) -> str:
    """Build /link message."""
    name = firm.get("name", "Firma")
    affiliate = firm.get("affiliate_url", "")
    slug = firm.get("slug", "")

    msg = f"{'━' * 28}\n"
    msg += f"  🔗 {name} — Güncel Giriş\n"
    msg += f"{'━' * 28}\n\n"

    msg += "Aşağıdaki butondan <b>güncel ve güvenli</b>\n"
    msg += "giriş adresine ulaşabilirsiniz.\n\n"

    msg += "✅ Link her zaman <b>günceldir</b>\n"
    msg += "✅ SSL korumalı güvenli bağlantı\n"
    msg += "✅ Hızlı erişim, yönlendirme yok\n\n"

    msg += f"{'─' * 28}\n"
    msg += "📌 Yeni link için tekrar /link yazabilirsiniz\n"

    buttons = []
    if affiliate:
        buttons.append([{"text": "🚀 Giriş Yap", "url": affiliate}])
    if slug:
        buttons.append([{"text": "📖 Site İncelemesi", "url": f"https://guncelgiris.ai/{slug}"}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    return msg, reply_markup


def build_destek_message(firm: dict) -> str:
    """Build /destek message."""
    name = firm.get("name", "Firma")
    affiliate = firm.get("affiliate_url", "")

    msg = f"{'━' * 28}\n"
    msg += f"  📞 {name} — Destek\n"
    msg += f"{'━' * 28}\n\n"

    msg += "<b>Canlı Destek Adımları:</b>\n\n"
    msg += "  1️⃣  Siteye giriş yapın\n"
    msg += "  2️⃣  Sağ alttaki canlı destek butonuna tıklayın\n"
    msg += "  3️⃣  7/24 Türkçe destek alın\n\n"

    msg += "<b>Sık Sorulan Konular:</b>\n\n"
    msg += "  💳  Para yatırma / çekme\n"
    msg += "  🎁  Bonus aktivasyonu\n"
    msg += "  🔑  Şifre sıfırlama\n"
    msg += "  📱  Mobil uygulama\n\n"

    msg += f"{'─' * 28}\n"
    msg += "🌐 <b>Bilgi portalı:</b> guncelgiris.ai\n"

    buttons = []
    if affiliate:
        buttons.append([{"text": "🔗 Siteye Git — Canlı Destek", "url": affiliate}])
    buttons.append([{"text": "🌐 guncelgiris.ai", "url": "https://guncelgiris.ai"}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    return msg, reply_markup


# ── Telethon: BotFather Automation ──

async def create_bot_via_botfather(api_id: int, api_hash: str, firm_name: str, bot_username: str) -> Optional[str]:
    """Create a bot via BotFather using Telethon. Returns bot token or None."""
    try:
        from telethon import TelegramClient

        session_file = SESSION_PATH
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()

        entity = await client.get_entity("@BotFather")

        # Send /newbot command
        await client.send_message(entity, "/newbot")
        await asyncio.sleep(3)

        # Read response (asks for bot name)
        messages = await client.get_messages(entity, limit=1)
        logger.info(f"BotFather response 1: {messages[0].text[:100]}")

        # Send bot display name
        display_name = f"{firm_name} Güncel Giriş 2026"
        if len(display_name) > 64:
            display_name = display_name[:64]
        await client.send_message(entity, display_name)
        await asyncio.sleep(3)

        # Read response (asks for username)
        messages = await client.get_messages(entity, limit=1)
        logger.info(f"BotFather response 2: {messages[0].text[:100]}")

        # Send bot username
        await client.send_message(entity, bot_username)
        await asyncio.sleep(3)

        # Read response (should contain token)
        messages = await client.get_messages(entity, limit=1)
        response_text = messages[0].text
        logger.info(f"BotFather response 3: {response_text[:200]}")

        # Extract token from response
        token_match = re.search(r'(\d+:[A-Za-z0-9_-]{35,})', response_text)
        if token_match:
            token = token_match.group(1)
            await client.disconnect()
            return token

        # If username was taken, BotFather says "Sorry, this username is already taken"
        if "already taken" in response_text.lower() or "already been taken" in response_text.lower():
            logger.warning(f"Username {bot_username} already taken")
            await client.disconnect()
            return None

        logger.error(f"Could not extract token from BotFather response: {response_text}")
        await client.disconnect()
        return None

    except Exception as e:
        logger.error(f"Error creating bot {bot_username}: {e}")
        return None


async def create_bot_via_botfather_with_session(client, firm_name: str, bot_username: str) -> Optional[str]:
    """Create a bot using existing Telethon client session (for bulk operations)."""
    try:
        entity = await client.get_entity("@BotFather")

        # Cancel any pending operation
        await client.send_message(entity, "/cancel")
        await asyncio.sleep(1)

        # Send /newbot command
        await client.send_message(entity, "/newbot")
        await asyncio.sleep(3)

        # Send bot display name
        display_name = f"{firm_name} Güncel Giriş 2026"
        if len(display_name) > 64:
            display_name = display_name[:64]
        await client.send_message(entity, display_name)
        await asyncio.sleep(3)

        # Read response
        messages = await client.get_messages(entity, limit=1)

        # Send bot username
        await client.send_message(entity, bot_username)
        await asyncio.sleep(4)

        # Read response with token
        messages = await client.get_messages(entity, limit=1)
        response_text = messages[0].text

        # Extract token
        token_match = re.search(r'(\d+:[A-Za-z0-9_-]{35,})', response_text)
        if token_match:
            return token_match.group(1)

        if "already taken" in response_text.lower() or "already been taken" in response_text.lower():
            logger.warning(f"Username {bot_username} already taken")
            return "TAKEN"

        logger.error(f"No token found for {bot_username}: {response_text[:200]}")
        return None

    except Exception as e:
        logger.error(f"Error creating bot {bot_username}: {e}")
        return None
