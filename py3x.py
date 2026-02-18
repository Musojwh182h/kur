import asyncio
import os
from datetime import UTC, datetime, timedelta

from dotenv import find_dotenv, load_dotenv
from remnawave import RemnawaveSDK
from remnawave.models.users import CreateUserRequestDto


load_dotenv(find_dotenv())

REMNAWAVE_BASE_URL = os.getenv("REMNAWAVE_BASE_URL") or os.getenv("PANEL_URL")
REMNAWAVE_TOKEN = os.getenv("REMNAWAVE_TOKEN") or os.getenv("API_TOKEN")

if not REMNAWAVE_BASE_URL or not REMNAWAVE_TOKEN:
    raise RuntimeError(
        "Не заданы REMNAWAVE_BASE_URL/REMNAWAVE_TOKEN (или PANEL_URL/API_TOKEN)."
    )

rem = RemnawaveSDK(base_url=REMNAWAVE_BASE_URL, token=REMNAWAVE_TOKEN)


async def create_or_get_user_by_tg(tg_id: int):
    users_response = await rem.users.get_all_users()
    username = str(tg_id)

    for user in users_response.users:
        if getattr(user, "username", None) == username:
            return user

    expire_date = datetime.now(UTC) + timedelta(days=30)
    create_body = CreateUserRequestDto(
        username=username,
        expire_at=expire_date,
        traffic_limit_bytes=50 * 1024**3,
        telegram_id=tg_id,
    )
    return await rem.users.create_user(create_body)


async def get_vpn_subscription(tg_id: int) -> str:
    user = await create_or_get_user_by_tg(tg_id)
    subscription = await rem.subscriptions.get_subscription_by_uuid(str(user.uuid))
    return subscription.subscription_url


async def main():
    telegram_id = 123456789
    link = await get_vpn_subscription(telegram_id)
    print("VPN subscription URL:", link)


if __name__ == "__main__":
    asyncio.run(main())