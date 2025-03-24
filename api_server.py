#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 商业版
API基础框架
"""

import os
import sys
import json
import time
import uuid
import datetime
from typing import Dict, List, Optional, Union, Any
from flask import Flask, request, jsonify, g
from functools import wraps

# 导入认证管理器
from auth_manager import AuthManager

# 创建Flask应用
app = Flask(__name__)

# 创建认证管理器实例
auth_manager = AuthManager()

# API版本
API_VERSION = "v1"

# API基础路径
API_BASE = f"/api/{API_VERSION}"

# 请求限流配置
RATE_LIMIT = {
    "default": 100,  # 默认每分钟请求数
    "auth": 20,      # 认证相关接口每分钟请求数
    "user": 50,      # 用户管理接口每分钟请求数
    "storage": 200   # 存储相关接口每分钟请求数
}

# 请求计数器
request_counters = {}

def rate_limit(limit_type="default"):
    """
    请求限流装饰器
    
    参数:
        limit_type: 限流类型，对应RATE_LIMIT中的键
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.remote_addr
            
            # 获取当前时间（分钟级别）
            current_minute = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 创建计数器键
            counter_key = f"{client_ip}:{limit_type}:{current_minute}"
            
            # 获取当前计数
            current_count = request_counters.get(counter_key, 0)
            
            # 获取限流阈值
            limit = RATE_LIMIT.get(limit_type, RATE_LIMIT["default"])
            
            # 检查是否超过限流阈值
            if current_count >= limit:
                return jsonify({
                    "status": "error",
                    "message": "请求过于频繁，请稍后再试",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }), 429
            
            # 更新计数器
            request_counters[counter_key] = current_count + 1
            
            # 执行原函数
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(permission=None):
    """
    认证和授权装饰器
    
    参数:
        permission: 所需权限，如果为None则只检查认证
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取认证头
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({
                    "status": "error",
                    "message": "未提供有效的认证信息",
                    "error_code": "UNAUTHORIZED"
                }), 401
            
            # 获取会话ID
            session_id = auth_header.split(" ")[1]
            
            # 获取用户
            user = auth_manager.get_user_from_session(session_id)
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "会话无效或已过期",
                    "error_code": "INVALID_SESSION"
                }), 401
            
            # 检查权限
            if permission and not auth_manager.check_permission(session_id, permission):
                return jsonify({
                    "status": "error",
                    "message": "没有足够的权限执行此操作",
                    "error_code": "PERMISSION_DENIED"
                }), 403
            
            # 将用户和会话ID存储在g对象中，以便在视图函数中使用
            g.user = user
            g.session_id = session_id
            
            # 执行原函数
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 定期清理过期的请求计数器
def cleanup_request_counters():
    """清理过期的请求计数器"""
    current_time = datetime.datetime.now()
    expired_keys = []
    
    for key in request_counters:
        # 解析键中的时间
        try:
            key_parts = key.split(":")
            if len(key_parts) >= 3:
                key_time_str = key_parts[2]
                key_time = datetime.datetime.strptime(key_time_str, "%Y-%m-%d %H:%M")
                
                # 如果时间差超过5分钟，则标记为过期
                if (current_time - key_time).total_seconds() > 300:
                    expired_keys.append(key)
        except:
            # 如果解析失败，也标记为过期
            expired_keys.append(key)
    
    # 删除过期的键
    for key in expired_keys:
        if key in request_counters:
            del request_counters[key]

# 设置定期执行清理任务
import threading
def start_cleanup_thread():
    """启动清理线程"""
    cleanup_request_counters()
    # 每5分钟执行一次清理
    threading.Timer(300, start_cleanup_thread).start()

# 启动清理线程
start_cleanup_thread()

# 认证相关API
@app.route(f"{API_BASE}/auth/login", methods=["POST"])
@rate_limit("auth")
def login():
    """用户登录API"""
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "无效的请求数据",
            "error_code": "INVALID_REQUEST"
        }), 400
    
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "用户名和密码不能为空",
            "error_code": "MISSING_CREDENTIALS"
        }), 400
    
    # 尝试登录
    session_id = auth_manager.login(username, password)
    if not session_id:
        return jsonify({
            "status": "error",
            "message": "用户名或密码错误",
            "error_code": "INVALID_CREDENTIALS"
        }), 401
    
    # 获取用户信息
    user = auth_manager.get_user_from_session(session_id)
    
    return jsonify({
        "status": "success",
        "message": "登录成功",
        "data": {
            "session_id": session_id,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "roles": user.roles
            }
        }
    })

@app.route(f"{API_BASE}/auth/logout", methods=["POST"])
@rate_limit("auth")
@require_auth()
def logout():
    """用户登出API"""
    # 从g对象中获取会话ID
    session_id = g.session_id
    
    # 尝试登出
    success = auth_manager.logout(session_id)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "登出成功"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "登出失败",
            "error_code": "LOGOUT_FAILED"
        }), 500

@app.route(f"{API_BASE}/auth/user-info", methods=["GET"])
@rate_limit("auth")
@require_auth()
def user_info():
    """获取当前用户信息API"""
    # 从g对象中获取用户
    user = g.user
    
    return jsonify({
        "status": "success",
        "message": "获取用户信息成功",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
            "roles": user.roles
        }
    })

# 用户管理API
@app.route(f"{API_BASE}/users", methods=["GET"])
@rate_limit("user")
@require_auth("user:read")
def list_users():
    """列出所有用户API"""
    users = auth_manager.list_users()
    
    return jsonify({
        "status": "success",
        "message": "获取用户列表成功",
        "data": {
            "users": users,
            "total": len(users)
        }
    })

@app.route(f"{API_BASE}/users", methods=["POST"])
@rate_limit("user")
@require_auth("user:create")
def create_user():
    """创建用户API"""
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "无效的请求数据",
            "error_code": "INVALID_REQUEST"
        }), 400
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    roles = data.get("roles", [])
    
    if not username or not email or not password:
        return jsonify({
            "status": "error",
            "message": "用户名、电子邮件和密码不能为空",
            "error_code": "MISSING_REQUIRED_FIELDS"
        }), 400
    
    # 创建用户
    user = auth_manager.create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        roles=roles
    )
    
    if not user:
        return jsonify({
            "status": "error",
            "message": "创建用户失败，用户名或电子邮件可能已存在",
            "error_code": "USER_CREATION_FAILED"
        }), 400
    
    return jsonify({
        "status": "success",
        "message": "创建用户成功",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "roles": user.roles
        }
    }), 201

@app.route(f"{API_BASE}/users/<user_id>", methods=["GET"])
@rate_limit("user")
@require_auth("user:read")
def get_user(user_id):
    """获取用户信息API"""
    user = auth_manager.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            "status": "error",
            "message": "用户不存在",
            "error_code": "USER_NOT_FOUND"
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "获取用户信息成功",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
            "roles": user.roles
        }
    })

@app.route(f"{API_BASE}/users/<user_id>", methods=["PUT"])
@rate_limit("user")
@require_auth("user:update")
def update_user(user_id):
    """更新用户信息API"""
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "无效的请求数据",
            "error_code": "INVALID_REQUEST"
        }), 400
    
    # 获取要更新的字段
    update_fields = {}
    
    if "email" in data:
        update_fields["email"] = data["email"]
    
    if "full_name" in data:
        update_fields["full_name"] = data["full_name"]
    
    if "is_active" in data:
        update_fields["is_active"] = data["is_active"]
    
    if "password" in data:
        # 对新密码进行哈希处理
        update_fields["password_hash"] = auth_manager.hash_password(data["password"])
    
    if "roles" in data:
        # 检查角色是否存在
        for role_name in data["roles"]:
            if not auth_manager.get_role(role_name):
                return jsonify({
                    "status": "error",
                    "message": f"角色不存在: {role_name}",
                    "error_code": "ROLE_NOT_FOUND"
                }), 400
        
        # 获取用户
        user = auth_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                "status": "error",
                "message": "用户不存在",
                "error_code": "USER_NOT_FOUND"
            }), 404
        
        # 更新角色
        user.roles = data["roles"]
    
    # 更新用户
    success = auth_manager.update_user(user_id, **update_fields)
    
    if not success:
        return jsonify({
            "status": "error",
            "message": "更新用户失败，用户可能不存在",
            "error_code": "USER_UPDATE_FAILED"
        }), 400
    
    # 获取更新后的用户信息
    user = auth_manager.get_user_by_id(user_id)
    
    return jsonify({
        "status": "success",
        "message": "更新用户成功",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": user.roles
        }
    })

@app.route(f"{API_BASE}/users/<user_id>", methods=["DELETE"])
@rate_limit("user")
@require_auth("user:delete")
def delete_user(user_id):
    """删除用户API"""
    # 不允许删除自己
    if g.user.user_id == user_id:
        return jsonify({
            "status": "error",
            "message": "不能删除当前登录的用户",
            "error_code": "CANNOT_DELETE_SELF"
        }), 400
    
    # 删除用户
    success = auth_manager.delete_user(user_id)
    
    if not success:
        return jsonify({
            "status": "error",
            "message": "删除用户失败，用户可能不存在",
            "error_code": "USER_DELETION_FAILED"
        }), 400
    
    return jsonify({
        "status": "success",
        "message": "删除用户成功"
    })

# 角色管理API
@app.route(f"{API_BASE}/roles", methods=["GET"])
@rate_limit("user")
@require_auth("role:read")
def list_roles():
    """列出所有角色API"""
    roles = auth_manager.list_roles()
    
    return jsonify({
        "status": "success",
        "message": "获取角色列表成功",
        "data": {
            "roles": roles,
            "total": len(roles)
        }
    })

@app.route(f"{API_BASE}/roles", methods=["POST"])
@rate_limit("user")
@require_auth("role:create")
def create_role():
    """创建角色API"""
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "无效的请求数据",
            "error_code": "INVALID_REQUEST"
        }), 400
    
    name = data.get("name")
    description = data.get("description")
    permissions = data.get("permissions", [])
    
    if not name:
        return jsonify({
            "status": "error",
            "message": "角色名称不能为空",
            "error_code": "MISSING_REQUIRED_FIELDS"
        }), 400
    
    # 创建角色
    role = auth_manager.create_role(
        name=name,
        description=description,
        permissions=permissions
    )
    
    if not role:
        return jsonify({
            "status": "error",
            "message": "创建角色失败，角色名称可能已存在",
            "error_code": "ROLE_CREATION_FAILED"
        }), 400
    
    return jsonify({
        "status": "success",
        "message": "创建角色成功",
        "data": {
            "role_id": role.role_id,
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions
        }
    }), 201

@app.route(f"{API_BASE}/roles/<name>", methods=["GET"])
@rate_limit("user")
@require_auth("role:read")
def get_role(name):
    """获取角色信息API"""
    role = auth_manager.get_role(name)
    
    if not role:
        return jsonify({
            "status": "error",
            "message": "角色不存在",
            "error_code": "ROLE_NOT_FOUND"
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "获取角色信息成功",
        "data": {
            "role_id": role.role_id,
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions
        }
    })

@app.route(f"{API_BASE}/roles/<name>", methods=["PUT"])
@rate_limit("user")
@require_auth("role:update")
def update_role(name):
    """更新角色信息API"""
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "无效的请求数据",
            "error_code": "INVALID_REQUEST"
        }), 400
    
    # 获取要更新的字段
    update_fields = {}
    
    if "description" in data:
        update_fields["description"] = data["description"]
    
    if "permissions" in data:
        update_fields["permissions"] = data["permissions"]
    
    # 更新角色
    success = auth_manager.update_role(name, **update_fields)
    
    if not success:
        return jsonify({
            "status": "error",
            "message": "更新角色失败，角色可能不存在",
            "error_code": "ROLE_UPDATE_FAILED"
        }), 400
    
    # 获取更新后的角色信息
    role = auth_manager.get_role(name)
    
    return jsonify({
        "status": "success",
        "message": "更新角色成功",
        "data": {
            "role_id": role.role_id,
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions
        }
    })

@app.route(f"{API_BASE}/roles/<name>", methods=["DELETE"])
@rate_limit("user")
@require_auth("role:delete")
def delete_role(name):
    """删除角色API"""
    # 不允许删除admin角色
    if name == "admin":
        return jsonify({
            "status": "error",
            "message": "不能删除admin角色",
            "error_code": "CANNOT_DELETE_ADMIN_ROLE"
        }), 400
    
    # 删除角色
    success = auth_manager.delete_role(name)
    
    if not success:
        return jsonify({
            "status": "error",
            "message": "删除角色失败，角色可能不存在",
            "error_code": "ROLE_DELETION_FAILED"
        }), 400
    
    return jsonify({
        "status": "success",
        "message": "删除角色成功"
    })

# 系统信息API
@app.route(f"{API_BASE}/system/info", methods=["GET"])
@rate_limit("default")
def system_info():
    """获取系统信息API"""
    return jsonify({
        "status": "success",
        "message": "获取系统信息成功",
        "data": {
            "name": "华为云存储服务控制系统",
            "version": "2.0.0",
            "api_version": API_VERSION,
            "build_date": "2025-03-24",
            "environment": "production"
        }
    })

# 健康检查API
@app.route(f"{API_BASE}/health", methods=["GET"])
def health_check():
    """健康检查API"""
    return jsonify({
        "status": "success",
        "message": "系统正常运行",
        "data": {
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {
                "api": "healthy",
                "auth": "healthy",
                "database": "healthy"
            }
        }
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        "status": "error",
        "message": "请求的资源不存在",
        "error_code": "NOT_FOUND"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    return jsonify({
        "status": "error",
        "message": "不支持的请求方法",
        "error_code": "METHOD_NOT_ALLOWED"
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    """处理500错误"""
    return jsonify({
        "status": "error",
        "message": "服务器内部错误",
        "error_code": "INTERNAL_SERVER_ERROR"
    }), 500

# 主函数
if __name__ == "__main__":
    # 设置主机和端口
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", 5000))
    
    # 设置调试模式
    debug = os.environ.get("API_DEBUG", "false").lower() == "true"
    
    print(f"启动API服务器，监听地址: {host}:{port}，调试模式: {debug}")
    app.run(host=host, port=port, debug=debug)
