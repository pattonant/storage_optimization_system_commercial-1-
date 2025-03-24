#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 商业版
用户认证与权限管理模块
"""

import os
import sys
import json
import time
import uuid
import hashlib
import datetime
from typing import Dict, List, Optional, Union, Any

class User:
    """用户类，表示系统中的一个用户账户"""
    
    def __init__(self, username: str, email: str, password_hash: str, 
                 user_id: str = None, full_name: str = None, 
                 created_at: datetime.datetime = None, 
                 last_login: datetime.datetime = None,
                 is_active: bool = True):
        """
        初始化用户对象
        
        参数:
            username: 用户名
            email: 电子邮件
            password_hash: 密码哈希值
            user_id: 用户ID，如果不提供则自动生成
            full_name: 用户全名
            created_at: 创建时间，如果不提供则使用当前时间
            last_login: 最后登录时间
            is_active: 是否激活
        """
        self.user_id = user_id if user_id else str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.created_at = created_at if created_at else datetime.datetime.now()
        self.last_login = last_login
        self.is_active = is_active
        self.roles = []  # 用户角色列表
    
    def to_dict(self) -> Dict[str, Any]:
        """将用户对象转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'roles': self.roles
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象"""
        created_at = datetime.datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        last_login = datetime.datetime.fromisoformat(data['last_login']) if data.get('last_login') else None
        
        user = cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            user_id=data['user_id'],
            full_name=data.get('full_name'),
            created_at=created_at,
            last_login=last_login,
            is_active=data.get('is_active', True)
        )
        user.roles = data.get('roles', [])
        return user
    
    def add_role(self, role_name: str) -> None:
        """添加角色到用户"""
        if role_name not in self.roles:
            self.roles.append(role_name)
    
    def remove_role(self, role_name: str) -> None:
        """从用户中移除角色"""
        if role_name in self.roles:
            self.roles.remove(role_name)
    
    def has_role(self, role_name: str) -> bool:
        """检查用户是否拥有指定角色"""
        return role_name in self.roles
    
    def update_last_login(self) -> None:
        """更新最后登录时间"""
        self.last_login = datetime.datetime.now()


class Role:
    """角色类，表示系统中的一个角色"""
    
    def __init__(self, name: str, description: str = None, 
                 permissions: List[str] = None, role_id: str = None):
        """
        初始化角色对象
        
        参数:
            name: 角色名称
            description: 角色描述
            permissions: 权限列表
            role_id: 角色ID，如果不提供则自动生成
        """
        self.role_id = role_id if role_id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.permissions = permissions if permissions else []
    
    def to_dict(self) -> Dict[str, Any]:
        """将角色对象转换为字典"""
        return {
            'role_id': self.role_id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """从字典创建角色对象"""
        return cls(
            name=data['name'],
            description=data.get('description'),
            permissions=data.get('permissions', []),
            role_id=data['role_id']
        )
    
    def add_permission(self, permission: str) -> None:
        """添加权限到角色"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """从角色中移除权限"""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission: str) -> bool:
        """检查角色是否拥有指定权限"""
        return permission in self.permissions


class AuthManager:
    """认证管理器，处理用户认证和权限管理"""
    
    def __init__(self, users_file: str = 'users.json', roles_file: str = 'roles.json'):
        """
        初始化认证管理器
        
        参数:
            users_file: 用户数据文件路径
            roles_file: 角色数据文件路径
        """
        self.users_file = users_file
        self.roles_file = roles_file
        self.users = {}  # 用户字典，键为用户ID
        self.roles = {}  # 角色字典，键为角色名称
        self.sessions = {}  # 会话字典，键为会话ID
        
        # 加载用户和角色数据
        self.load_data()
        
        # 如果没有角色，创建默认角色
        if not self.roles:
            self._create_default_roles()
        
        # 如果没有用户，创建管理员用户
        if not self.users:
            self._create_admin_user()
    
    def load_data(self) -> None:
        """加载用户和角色数据"""
        # 加载用户数据
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
            except Exception as e:
                print(f"加载用户数据失败: {str(e)}")
        
        # 加载角色数据
        if os.path.exists(self.roles_file):
            try:
                with open(self.roles_file, 'r', encoding='utf-8') as f:
                    roles_data = json.load(f)
                    for role_data in roles_data:
                        role = Role.from_dict(role_data)
                        self.roles[role.name] = role
            except Exception as e:
                print(f"加载角色数据失败: {str(e)}")
    
    def save_data(self) -> None:
        """保存用户和角色数据"""
        # 保存用户数据
        try:
            users_data = [user.to_dict() for user in self.users.values()]
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=4)
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
        
        # 保存角色数据
        try:
            roles_data = [role.to_dict() for role in self.roles.values()]
            with open(self.roles_file, 'w', encoding='utf-8') as f:
                json.dump(roles_data, f, indent=4)
        except Exception as e:
            print(f"保存角色数据失败: {str(e)}")
    
    def _create_default_roles(self) -> None:
        """创建默认角色"""
        # 管理员角色
        admin_role = Role(
            name="admin",
            description="系统管理员，拥有所有权限",
            permissions=["user:create", "user:read", "user:update", "user:delete",
                        "role:create", "role:read", "role:update", "role:delete",
                        "system:config", "system:backup", "system:restore",
                        "storage:read", "storage:write", "storage:optimize"]
        )
        self.roles[admin_role.name] = admin_role
        
        # 操作员角色
        operator_role = Role(
            name="operator",
            description="系统操作员，拥有操作权限",
            permissions=["storage:read", "storage:write", "storage:optimize"]
        )
        self.roles[operator_role.name] = operator_role
        
        # 只读用户角色
        readonly_role = Role(
            name="readonly",
            description="只读用户，只拥有读取权限",
            permissions=["storage:read"]
        )
        self.roles[readonly_role.name] = readonly_role
        
        # 保存角色数据
        self.save_data()
    
    def _create_admin_user(self) -> None:
        """创建管理员用户"""
        # 生成随机密码
        admin_password = str(uuid.uuid4())[:8]
        password_hash = self.hash_password(admin_password)
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=password_hash,
            full_name="System Administrator"
        )
        admin_user.add_role("admin")
        
        # 添加到用户字典
        self.users[admin_user.user_id] = admin_user
        
        # 保存用户数据
        self.save_data()
        
        # 打印管理员密码
        print("=" * 50)
        print("已创建管理员用户:")
        print(f"用户名: admin")
        print(f"密码: {admin_password}")
        print("请妥善保管此密码，首次登录后请立即修改。")
        print("=" * 50)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理
        
        参数:
            password: 原始密码
            
        返回:
            str: 密码哈希值
        """
        # 使用SHA-256算法对密码进行哈希
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        验证密码是否匹配哈希值
        
        参数:
            password: 原始密码
            password_hash: 密码哈希值
            
        返回:
            bool: 密码是否匹配
        """
        return self.hash_password(password) == password_hash
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, roles: List[str] = None) -> Optional[User]:
        """
        创建新用户
        
        参数:
            username: 用户名
            email: 电子邮件
            password: 密码
            full_name: 用户全名
            roles: 角色列表
            
        返回:
            Optional[User]: 创建的用户对象，如果创建失败则返回None
        """
        # 检查用户名是否已存在
        for user in self.users.values():
            if user.username == username:
                print(f"用户名已存在: {username}")
                return None
        
        # 检查电子邮件是否已存在
        for user in self.users.values():
            if user.email == email:
                print(f"电子邮件已存在: {email}")
                return None
        
        # 对密码进行哈希处理
        password_hash = self.hash_password(password)
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        
        # 添加角色
        if roles:
            for role_name in roles:
                if role_name in self.roles:
                    user.add_role(role_name)
                else:
                    print(f"角色不存在: {role_name}")
        
        # 添加到用户字典
        self.users[user.user_id] = user
        
        # 保存用户数据
        self.save_data()
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据用户ID获取用户
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        参数:
            username: 用户名
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据电子邮件获取用户
        
        参数:
            email: 电子邮件
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """
        更新用户信息
        
        参数:
            user_id: 用户ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        user = self.get_user_by_id(user_id)
        if not user:
            print(f"用户不存在: {user_id}")
            return False
        
        # 更新用户字段
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        # 保存用户数据
        self.save_data()
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        参数:
            user_id: 用户ID
            
        返回:
            bool: 是否删除成功
        """
        if user_id in self.users:
            del self.users[user_id]
            self.save_data()
            return True
        else:
            print(f"用户不存在: {user_id}")
            return False
    
    def create_role(self, name: str, description: str = None, 
                   permissions: List[str] = None) -> Optional[Role]:
        """
        创建新角色
        
        参数:
            name: 角色名称
            description: 角色描述
            permissions: 权限列表
            
        返回:
            Optional[Role]: 创建的角色对象，如果创建失败则返回None
        """
        # 检查角色名称是否已存在
        if name in self.roles:
            print(f"角色名称已存在: {name}")
            return None
        
        # 创建新角色
        role = Role(
            name=name,
            description=description,
            permissions=permissions
        )
        
        # 添加到角色字典
        self.roles[role.name] = role
        
        # 保存角色数据
        self.save_data()
        
        return role
    
    def get_role(self, name: str) -> Optional[Role]:
        """
        获取角色
        
        参数:
            name: 角色名称
            
        返回:
            Optional[Role]: 角色对象，如果不存在则返回None
        """
        return self.roles.get(name)
    
    def update_role(self, name: str, **kwargs) -> bool:
        """
        更新角色信息
        
        参数:
            name: 角色名称
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        role = self.get_role(name)
        if not role:
            print(f"角色不存在: {name}")
            return False
        
        # 更新角色字段
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        # 保存角色数据
        self.save_data()
        
        return True
    
    def delete_role(self, name: str) -> bool:
        """
        删除角色
        
        参数:
            name: 角色名称
            
        返回:
            bool: 是否删除成功
        """
        if name in self.roles:
            # 从所有用户中移除该角色
            for user in self.users.values():
                if name in user.roles:
                    user.roles.remove(name)
            
            # 删除角色
            del self.roles[name]
            
            # 保存数据
            self.save_data()
            
            return True
        else:
            print(f"角色不存在: {name}")
            return False
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        用户登录
        
        参数:
            username: 用户名
            password: 密码
            
        返回:
            Optional[str]: 会话ID，如果登录失败则返回None
        """
        # 获取用户
        user = self.get_user_by_username(username)
        if not user:
            print(f"用户不存在: {username}")
            return None
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            print("密码错误")
            return None
        
        # 检查用户是否激活
        if not user.is_active:
            print("用户未激活")
            return None
        
        # 更新最后登录时间
        user.update_last_login()
        self.save_data()
        
        # 创建会话
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'user_id': user.user_id,
            'created_at': datetime.datetime.now(),
            'expires_at': datetime.datetime.now() + datetime.timedelta(hours=24)
        }
        
        return session_id
    
    def logout(self, session_id: str) -> bool:
        """
        用户登出
        
        参数:
            session_id: 会话ID
            
        返回:
            bool: 是否登出成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        else:
            print(f"会话不存在: {session_id}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        参数:
            session_id: 会话ID
            
        返回:
            Optional[Dict[str, Any]]: 会话信息，如果不存在则返回None
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # 检查会话是否过期
        if session['expires_at'] < datetime.datetime.now():
            del self.sessions[session_id]
            return None
        
        return session
    
    def get_user_from_session(self, session_id: str) -> Optional[User]:
        """
        从会话中获取用户
        
        参数:
            session_id: 会话ID
            
        返回:
            Optional[User]: 用户对象，如果会话不存在或已过期则返回None
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return self.get_user_by_id(session['user_id'])
    
    def check_permission(self, session_id: str, permission: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        参数:
            session_id: 会话ID
            permission: 权限名称
            
        返回:
            bool: 用户是否拥有权限
        """
        # 获取用户
        user = self.get_user_from_session(session_id)
        if not user:
            return False
        
        # 检查用户角色
        for role_name in user.roles:
            role = self.get_role(role_name)
            if role and role.has_permission(permission):
                return True
        
        return False
    
    def list_users(self) -> List[Dict[str, Any]]:
        """
        列出所有用户
        
        返回:
            List[Dict[str, Any]]: 用户信息列表
        """
        return [
            {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'roles': user.roles
            }
            for user in self.users.values()
        ]
    
    def list_roles(self) -> List[Dict[str, Any]]:
        """
        列出所有角色
        
        返回:
            List[Dict[str, Any]]: 角色信息列表
        """
        return [
            {
                'role_id': role.role_id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions
            }
            for role in self.roles.values()
        ]


# 测试代码
if __name__ == "__main__":
    # 创建认证管理器
    auth_manager = AuthManager()
    
    # 创建测试用户
    test_user = auth_manager.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        roles=["operator"]
    )
    
    if test_user:
        print(f"创建用户成功: {test_user.username}")
    
    # 测试登录
    session_id = auth_manager.login("testuser", "password123")
    if session_id:
        print(f"登录成功，会话ID: {session_id}")
        
        # 测试权限检查
        has_permission = auth_manager.check_permission(session_id, "storage:read")
        print(f"用户是否拥有storage:read权限: {has_permission}")
        
        # 测试登出
        logout_success = auth_manager.logout(session_id)
        print(f"登出成功: {logout_success}")
    
    # 列出所有用户
    users = auth_manager.list_users()
    print(f"系统中的用户数量: {len(users)}")
    
    # 列出所有角色
    roles = auth_manager.list_roles()
    print(f"系统中的角色数量: {len(roles)}")
