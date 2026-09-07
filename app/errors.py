class AppError(Exception):
    status = 400

class NotFound(AppError):
    status = 404

class Conflict(AppError):
    status = 409

class Forbidden(AppError):
    status = 403

class Unauthorized(AppError):
    status = 401
