import time
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Item


def purchase(db: Session, item_id: str, cash_inserted: int) -> dict:
    # item = db.query(Item).filter(Item.id == item_id).first()
    item = db.query(Item).with_for_update().filter(Item.id == item_id).first()

    if not item:
        raise ValueError("item_not_found")
    time.sleep(0.05)  # demo: widens race window for concurrent purchase/restock
    # if two users purchases same time it will allow both to purchase even if there is only 1 item left. This is because we are not locking the item record for update, so both transactions read the same initial quantity before either of them updates it. This can lead to overselling if multiple purchases happen concurrently on the same item. To prevent this, we would need to implement some form of locking or use database transactions with appropriate isolation levels to ensure that only one purchase can proceed at a time for a given item.
    if item.quantity <= 0:
        raise ValueError("out_of_stock")
    if cash_inserted < item.price:
        raise ValueError("insufficient_cash", item.price, cash_inserted)
    # No validation that cash_inserted or change use SUPPORTED_DENOMINATIONS
    change = cash_inserted - item.price
    item.quantity -= 1
    # item solt might be null if item is not associated with any slot, so we need to check if item.slot is not None before accessing it
    # item.slot.current_item_count -= 1
    if item.slot:
        item.slot.current_item_count -= 1

    db.commit()
    db.refresh(item)
    return {
        "item": item.name,
        "price": item.price,
        "cash_inserted": cash_inserted,
        "change_returned": change,
        "remaining_quantity": item.quantity,
        "message": "Purchase successful",
    }


def change_breakdown(change: int) -> dict:
    denominations = sorted(settings.SUPPORTED_DENOMINATIONS, reverse=True)
    result: dict[str, int] = {}
    remaining = change
    for d in denominations:
        if remaining <= 0:
            break
        count = remaining // d
        if count > 0:
            result[str(d)] = count
            remaining -= count * d
    return {"change": change, "denominations": result}
