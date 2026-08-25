from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.orders import Order


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[Order]:
        """
        Recupera la lista paginata degli ordini di un utente, dal più recente al più vecchio.
        """
        stmt = (select(Order).where(Order.user_id == user_id).options(selectinload(Order.items))
                .order_by(desc(Order.created_at)).offset(skip).limit(limit))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # estrai la lista di tutti i risultati
    # scalar_one_or_none() estrae al massimo una riga
    # limit = quanti elementi vuoi leggere per singola richiesta (limit=20 restituisce una pagina di 20 ordini)
    # skip = quanti elementi saltare a partire dall'inizio dell'elenco (Se vuoi la Pagina 1: skip=0 (prendi da 1 a 20))
    # offset = è la sintassi SQL di skip



    async def get_order_by_id(self, order_id: UUID, user_id: UUID) -> Order | None:
        """
        Recupera un singolo ordine con i suoi articoli, verificando la proprietà dell'utente.
        """
        stmt = (select(Order).where(Order.id == order_id).where(Order.user_id == user_id)
                .options(selectinload(Order.items)))
        result = await self.db.execute(stmt)
        single_order = result.scalar_one_or_none()
        return single_order
