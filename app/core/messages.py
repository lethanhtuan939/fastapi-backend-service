from enum import StrEnum
from typing import Final
from fastapi import Header


class MessageCode(StrEnum):
    # Success - User
    USER_CREATED = "user.created"
    USER_RETRIEVED = "user.retrieved"
    USER_LIST_RETRIEVED = "user.list_retrieved"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"

    # Success - Auth
    LOGIN_SUCCESS = "auth.login_success"
    LOGOUT_SUCCESS = "auth.logout_success"
    REFRESH_TOKEN_SUCCESS = "auth.refresh_success"

    # Error - Common
    BAD_REQUEST = "common.bad_request"
    UNAUTHORIZED = "common.unauthorized"
    FORBIDDEN = "common.forbidden"
    NOT_FOUND = "common.not_found"
    INTERNAL_ERROR = "common.internal_error"
    VALIDATION_ERROR = "common.validation_error"

    # Error - User
    USER_NOT_FOUND = "user.not_found"
    USERNAME_EXISTS = "user.username_exists"


MESSAGES: Final[dict[str, dict[str, str]]] = {
    "vi": {
        # Success
        MessageCode.USER_CREATED: "Tạo người dùng thành công",
        MessageCode.USER_RETRIEVED: "Lấy thông tin người dùng thành công",
        MessageCode.USER_LIST_RETRIEVED: "Lấy danh sách người dùng thành công",
        MessageCode.USER_UPDATED: "Cập nhật người dùng thành công",
        MessageCode.USER_DELETED: "Xóa người dùng thành công",
        MessageCode.LOGIN_SUCCESS: "Đăng nhập thành công",
        MessageCode.LOGOUT_SUCCESS: "Đăng xuất thành công",
        # Error
        MessageCode.BAD_REQUEST: "Yêu cầu không hợp lệ",
        MessageCode.UNAUTHORIZED: "Chưa xác thực",
        MessageCode.FORBIDDEN: "Không có quyền truy cập",
        MessageCode.NOT_FOUND: "Không tìm thấy tài nguyên",
        MessageCode.INTERNAL_ERROR: "Lỗi hệ thống, vui lòng thử lại sau",
        MessageCode.VALIDATION_ERROR: "Dữ liệu không hợp lệ",
        MessageCode.USER_NOT_FOUND: "Không tìm thấy người dùng",
        MessageCode.USERNAME_EXISTS: "Tên người dùng đã tồn tại",
    },
    "en": {
        MessageCode.USER_CREATED: "User created successfully",
        MessageCode.USER_RETRIEVED: "User retrieved successfully",
        MessageCode.USER_LIST_RETRIEVED: "User list retrieved successfully",
        MessageCode.USER_UPDATED: "User updated successfully",
        MessageCode.USER_DELETED: "User deleted successfully",
        MessageCode.LOGIN_SUCCESS: "Login successful",
        MessageCode.LOGOUT_SUCCESS: "Logout successful",
        MessageCode.BAD_REQUEST: "Bad request",
        MessageCode.UNAUTHORIZED: "Unauthorized",
        MessageCode.FORBIDDEN: "Forbidden",
        MessageCode.NOT_FOUND: "Resource not found",
        MessageCode.INTERNAL_ERROR: "Internal server error",
        MessageCode.VALIDATION_ERROR: "Validation error",
        MessageCode.USER_NOT_FOUND: "User not found",
        MessageCode.USERNAME_EXISTS: "Username already exists",
    },
}


def get_message(code: MessageCode, lang: str = "vi"):
    lang = lang.split("-")[0]
    return MESSAGES.get(lang, MESSAGES["vi"]).get(code.value, code.value)
