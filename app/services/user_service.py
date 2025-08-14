class UserService:
    def __init__(self):
        # 실제로는 데이터베이스 연결
        self.users = [
            {"id": 1, "name": "김철수", "email": "kim@example.com"},
            {"id": 2, "name": "이영희", "email": "lee@example.com"}
        ]
    
    def get_all_users(self):
        return {"users": self.users, "total": len(self.users)}
    
    def get_user_by_id(self, user_id: int):
        user = next((u for u in self.users if u["id"] == user_id), None)
        return user if user else {"error": "사용자를 찾을 수 없습니다"}
    
    def create_user(self, name: str, email: str):
        new_id = max([u["id"] for u in self.users], default=0) + 1
        new_user = {"id": new_id, "name": name, "email": email}
        self.users.append(new_user)
        return {"message": "사용자 생성 완료", "user": new_user}
    
    def update_user(self, user_id: int, name: str, email: str):
        for user in self.users:
            if user["id"] == user_id:
                user["name"] = name
                user["email"] = email
                return {"message": "사용자 수정 완료", "user": user}
        return {"error": "사용자를 찾을 수 없습니다"}
    
    def delete_user(self, user_id: int):
        self.users = [u for u in self.users if u["id"] != user_id]
        return {"message": f"사용자 {user_id} 삭제 완료"}
