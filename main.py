from aiogram.utils import executor

from bot import dp
from hooks import shutdown, startup

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
