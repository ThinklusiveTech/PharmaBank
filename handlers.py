def user_helper(user) -> dict:
    """Convert MongoDB user to safe response (remove password)"""
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user