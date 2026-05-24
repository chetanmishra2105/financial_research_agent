import asyncio
from src.api.routes import get_workflow

async def main():
    wf = get_workflow()
    result = await wf.execute('Should I invest in NVIDIA for long-term growth?')
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
