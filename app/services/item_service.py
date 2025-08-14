class ItemService:
    def __init__(self):
        self.items = [
            {"id": 1, "name": "노트북", "price": 1500000, "category": "전자제품"},
            {"id": 2, "name": "마우스", "price": 50000, "category": "전자제품"}
        ]
    
    def get_all_items(self):
        return {"items": self.items, "total": len(self.items)}
    
    def get_item_by_id(self, item_id: int):
        item = next((i for i in self.items if i["id"] == item_id), None)
        return item if item else {"error": "상품을 찾을 수 없습니다"}
    
    def create_item(self, name: str, price: float, category: str):
        new_id = max([i["id"] for i in self.items], default=0) + 1
        new_item = {"id": new_id, "name": name, "price": price, "category": category}
        self.items.append(new_item)
        return {"message": "상품 생성 완료", "item": new_item}
    
    def update_item(self, item_id: int, name: str, price: float):
        for item in self.items:
            if item["id"] == item_id:
                item["name"] = name
                item["price"] = price
                return {"message": "상품 수정 완료", "item": item}
        return {"error": "상품을 찾을 수 없습니다"}
