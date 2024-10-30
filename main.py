import asyncio
from contextlib import suppress
import sys
from bot.launch import process



async def main():
    await process()


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(f"    🤖 До скорого, до следующего запуска <3")
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(0)