import asyncio
import sys
from bot.launch import process



async def main():
    await process()


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(f"    🤖 See you later, crypto farmer! Keep on clicking! 🌟")
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(0)