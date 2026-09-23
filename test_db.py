import asyncio
from sqlalchemy import text
from db.session import async_session_maker

async def main():
    async with async_session_maker() as session:
        # Всего услуг
        result = await session.execute(text("SELECT COUNT(*) FROM patient_groups"))
        total = result.scalar()
        print(f"Всего услуг в БД: {total}")
        
        # Published
        result = await session.execute(text("SELECT COUNT(*) FROM patient_groups WHERE status='published'"))
        published = result.scalar()
        print(f"Published услуг: {published}")
        
        # Все с деталями
        result = await session.execute(text("SELECT id, title, status FROM patient_groups"))
        print("\nВсе строки:")
        for row in result.all():
            print(f"  id={row[0]} | title={row[1]} | status={row[2]}")

asyncio.run(main())