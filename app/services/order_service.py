class OrderService:
    def __init__(self):
        self.orders = [
            {"id": 1, "user_id": 1, "item_id": 1, "quantity": 1, "status": "완료"},
            {"id": 2, "user_id": 2, "item_id": 2, "quantity": 2, "status": "진행중"}
        ]
    
    def get_all_orders(self):
        return {"orders": self.orders, "total": len(self.orders)}
    
    def get_order_by_id(self, order_id: int):
        order = next((o for o in self.orders if o["id"] == order_id), None)
        return order if order else {"error": "주문을 찾을 수 없습니다"}
    
    def create_order(self, user_id: int, item_id: int, quantity: int):
        new_id = max([o["id"] for o in self.orders], default=0) + 1
        new_order = {
            "id": new_id, 
            "user_id": user_id, 
            "item_id": item_id, 
            "quantity": quantity, 
            "status": "진행중"
        }
        self.orders.append(new_order)
        return {"message": "주문 생성 완료", "order": new_order}
