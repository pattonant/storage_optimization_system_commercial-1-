#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 商业版
数据库设计与实现
"""

import os
import sys
import json
import time
import uuid
import datetime
import sqlite3
from typing import Dict, List, Optional, Union, Any, Tuple

class Database:
    """数据库管理类，处理数据库连接和操作"""
    
    def __init__(self, db_file: str = 'storage_system.db'):
        """
        初始化数据库管理器
        
        参数:
            db_file: 数据库文件路径
        """
        self.db_file = db_file
        self.connection = None
        
        # 初始化数据库
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接
        
        返回:
            sqlite3.Connection: 数据库连接对象
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_file)
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂为字典
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close_connection(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self) -> None:
        """初始化数据库，创建必要的表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        ''')
        
        # 创建角色表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            role_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
        ''')
        
        # 创建权限表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
        ''')
        
        # 创建角色权限关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id TEXT NOT NULL,
            permission_id TEXT NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions (permission_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建用户角色关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建存储系统表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS storage_systems (
            system_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            disk_space REAL NOT NULL,
            token_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (user_id)
        )
        ''')
        
        # 创建存储对象表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS storage_objects (
            object_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            name TEXT NOT NULL,
            size REAL NOT NULL,
            access_frequency REAL NOT NULL,
            original_position INTEGER NOT NULL,
            current_position INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (system_id) REFERENCES storage_systems (system_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建优化任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS optimization_jobs (
            job_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            status TEXT NOT NULL,
            before_fragmentation REAL,
            after_fragmentation REAL,
            before_score REAL,
            after_score REAL,
            improvement REAL,
            time_cost REAL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            created_by TEXT NOT NULL,
            FOREIGN KEY (system_id) REFERENCES storage_systems (system_id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users (user_id)
        )
        ''')
        
        # 创建性能指标表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            metric_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            job_id TEXT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (system_id) REFERENCES storage_systems (system_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES optimization_jobs (job_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建系统配置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            config_key TEXT PRIMARY KEY,
            config_value TEXT NOT NULL,
            description TEXT,
            updated_at TEXT NOT NULL,
            updated_by TEXT,
            FOREIGN KEY (updated_by) REFERENCES users (user_id)
        )
        ''')
        
        # 创建审计日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
        )
        ''')
        
        # 创建计划任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            task_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            parameters TEXT,
            schedule TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            last_run TEXT,
            next_run TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (user_id)
        )
        ''')
        
        # 创建许可证表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_id TEXT PRIMARY KEY,
            license_key TEXT UNIQUE NOT NULL,
            license_type TEXT NOT NULL,
            features TEXT NOT NULL,
            issued_to TEXT NOT NULL,
            issued_at TEXT NOT NULL,
            expires_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        ''')
        
        # 创建会话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        ''')
        
        # 提交事务
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        执行查询语句
        
        参数:
            query: SQL查询语句
            params: 查询参数
            
        返回:
            List[Dict]: 查询结果列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        # 获取结果
        rows = cursor.fetchall()
        
        # 将结果转换为字典列表
        result = []
        for row in rows:
            result.append(dict(row))
        
        return result
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        执行更新语句
        
        参数:
            query: SQL更新语句
            params: 更新参数
            
        返回:
            int: 受影响的行数
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> str:
        """
        执行插入语句
        
        参数:
            query: SQL插入语句
            params: 插入参数
            
        返回:
            str: 最后插入的行ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.lastrowid
    
    def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> bool:
        """
        执行事务
        
        参数:
            queries: 查询列表，每个元素为(query, params)元组
            
        返回:
            bool: 事务是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.execute("BEGIN TRANSACTION")
            
            # 执行所有查询
            for query, params in queries:
                cursor.execute(query, params)
            
            # 提交事务
            conn.commit()
            
            return True
        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"事务执行失败: {str(e)}")
            return False


class UserRepository:
    """用户数据仓库，处理用户相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化用户数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_user(self, user_id: str, username: str, email: str, password_hash: str,
                   full_name: str = None, created_at: str = None, last_login: str = None,
                   is_active: bool = True) -> bool:
        """
        创建新用户
        
        参数:
            user_id: 用户ID
            username: 用户名
            email: 电子邮件
            password_hash: 密码哈希值
            full_name: 用户全名
            created_at: 创建时间，如果不提供则使用当前时间
            last_login: 最后登录时间
            is_active: 是否激活
            
        返回:
            bool: 是否创建成功
        """
        if not created_at:
            created_at = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO users (user_id, username, email, password_hash, full_name, created_at, last_login, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                user_id, username, email, password_hash, full_name, created_at,
                last_login, 1 if is_active else 0
            ))
            return True
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        根据用户ID获取用户
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[Dict]: 用户信息，如果不存在则返回None
        """
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,))
        
        if result:
            return result[0]
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        根据用户名获取用户
        
        参数:
            username: 用户名
            
        返回:
            Optional[Dict]: 用户信息，如果不存在则返回None
        """
        query = "SELECT * FROM users WHERE username = ?"
        result = self.db.execute_query(query, (username,))
        
        if result:
            return result[0]
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        根据电子邮件获取用户
        
        参数:
            email: 电子邮件
            
        返回:
            Optional[Dict]: 用户信息，如果不存在则返回None
        """
        query = "SELECT * FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        
        if result:
            return result[0]
        
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
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['username', 'email', 'password_hash', 'full_name', 'last_login', 'is_active']:
                set_clause.append(f"{key} = ?")
                # 对布尔值进行转换
                if key == 'is_active':
                    params.append(1 if value else 0)
                else:
                    params.append(value)
        
        if not set_clause:
            return False
        
        query = f"UPDATE users SET {', '.join(set_clause)} WHERE user_id = ?"
        params.append(user_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        参数:
            user_id: 用户ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM users WHERE user_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (user_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False
    
    def list_users(self) -> List[Dict]:
        """
        列出所有用户
        
        返回:
            List[Dict]: 用户信息列表
        """
        query = "SELECT * FROM users"
        return self.db.execute_query(query)
    
    def get_user_roles(self, user_id: str) -> List[Dict]:
        """
        获取用户的角色
        
        参数:
            user_id: 用户ID
            
        返回:
            List[Dict]: 角色信息列表
        """
        query = '''
        SELECT r.* FROM roles r
        JOIN user_roles ur ON r.role_id = ur.role_id
        WHERE ur.user_id = ?
        '''
        
        return self.db.execute_query(query, (user_id,))
    
    def add_user_role(self, user_id: str, role_id: str) -> bool:
        """
        为用户添加角色
        
        参数:
            user_id: 用户ID
            role_id: 角色ID
            
        返回:
            bool: 是否添加成功
        """
        query = "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)"
        
        try:
            self.db.execute_insert(query, (user_id, role_id))
            return True
        except Exception as e:
            print(f"为用户添加角色失败: {str(e)}")
            return False
    
    def remove_user_role(self, user_id: str, role_id: str) -> bool:
        """
        移除用户的角色
        
        参数:
            user_id: 用户ID
            role_id: 角色ID
            
        返回:
            bool: 是否移除成功
        """
        query = "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (user_id, role_id))
            return affected_rows > 0
        except Exception as e:
            print(f"移除用户角色失败: {str(e)}")
            return False
    
    def clear_user_roles(self, user_id: str) -> bool:
        """
        清除用户的所有角色
        
        参数:
            user_id: 用户ID
            
        返回:
            bool: 是否清除成功
        """
        query = "DELETE FROM user_roles WHERE user_id = ?"
        
        try:
            self.db.execute_update(query, (user_id,))
            return True
        except Exception as e:
            print(f"清除用户角色失败: {str(e)}")
            return False


class RoleRepository:
    """角色数据仓库，处理角色相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化角色数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_role(self, role_id: str, name: str, description: str = None) -> bool:
        """
        创建新角色
        
        参数:
            role_id: 角色ID
            name: 角色名称
            description: 角色描述
            
        返回:
            bool: 是否创建成功
        """
        query = "INSERT INTO roles (role_id, name, description) VALUES (?, ?, ?)"
        
        try:
            self.db.execute_insert(query, (role_id, name, description))
            return True
        except Exception as e:
            print(f"创建角色失败: {str(e)}")
            return False
    
    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        """
        根据角色ID获取角色
        
        参数:
            role_id: 角色ID
            
        返回:
            Optional[Dict]: 角色信息，如果不存在则返回None
        """
        query = "SELECT * FROM roles WHERE role_id = ?"
        result = self.db.execute_query(query, (role_id,))
        
        if result:
            return result[0]
        
        return None
    
    def get_role_by_name(self, name: str) -> Optional[Dict]:
        """
        根据角色名称获取角色
        
        参数:
            name: 角色名称
            
        返回:
            Optional[Dict]: 角色信息，如果不存在则返回None
        """
        query = "SELECT * FROM roles WHERE name = ?"
        result = self.db.execute_query(query, (name,))
        
        if result:
            return result[0]
        
        return None
    
    def update_role(self, role_id: str, **kwargs) -> bool:
        """
        更新角色信息
        
        参数:
            role_id: 角色ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'description']:
                set_clause.append(f"{key} = ?")
                params.append(value)
        
        if not set_clause:
            return False
        
        query = f"UPDATE roles SET {', '.join(set_clause)} WHERE role_id = ?"
        params.append(role_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新角色失败: {str(e)}")
            return False
    
    def delete_role(self, role_id: str) -> bool:
        """
        删除角色
        
        参数:
            role_id: 角色ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM roles WHERE role_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (role_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除角色失败: {str(e)}")
            return False
    
    def list_roles(self) -> List[Dict]:
        """
        列出所有角色
        
        返回:
            List[Dict]: 角色信息列表
        """
        query = "SELECT * FROM roles"
        return self.db.execute_query(query)
    
    def get_role_permissions(self, role_id: str) -> List[Dict]:
        """
        获取角色的权限
        
        参数:
            role_id: 角色ID
            
        返回:
            List[Dict]: 权限信息列表
        """
        query = '''
        SELECT p.* FROM permissions p
        JOIN role_permissions rp ON p.permission_id = rp.permission_id
        WHERE rp.role_id = ?
        '''
        
        return self.db.execute_query(query, (role_id,))
    
    def add_role_permission(self, role_id: str, permission_id: str) -> bool:
        """
        为角色添加权限
        
        参数:
            role_id: 角色ID
            permission_id: 权限ID
            
        返回:
            bool: 是否添加成功
        """
        query = "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)"
        
        try:
            self.db.execute_insert(query, (role_id, permission_id))
            return True
        except Exception as e:
            print(f"为角色添加权限失败: {str(e)}")
            return False
    
    def remove_role_permission(self, role_id: str, permission_id: str) -> bool:
        """
        移除角色的权限
        
        参数:
            role_id: 角色ID
            permission_id: 权限ID
            
        返回:
            bool: 是否移除成功
        """
        query = "DELETE FROM role_permissions WHERE role_id = ? AND permission_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (role_id, permission_id))
            return affected_rows > 0
        except Exception as e:
            print(f"移除角色权限失败: {str(e)}")
            return False
    
    def clear_role_permissions(self, role_id: str) -> bool:
        """
        清除角色的所有权限
        
        参数:
            role_id: 角色ID
            
        返回:
            bool: 是否清除成功
        """
        query = "DELETE FROM role_permissions WHERE role_id = ?"
        
        try:
            self.db.execute_update(query, (role_id,))
            return True
        except Exception as e:
            print(f"清除角色权限失败: {str(e)}")
            return False


class PermissionRepository:
    """权限数据仓库，处理权限相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化权限数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_permission(self, permission_id: str, name: str, description: str = None) -> bool:
        """
        创建新权限
        
        参数:
            permission_id: 权限ID
            name: 权限名称
            description: 权限描述
            
        返回:
            bool: 是否创建成功
        """
        query = "INSERT INTO permissions (permission_id, name, description) VALUES (?, ?, ?)"
        
        try:
            self.db.execute_insert(query, (permission_id, name, description))
            return True
        except Exception as e:
            print(f"创建权限失败: {str(e)}")
            return False
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Dict]:
        """
        根据权限ID获取权限
        
        参数:
            permission_id: 权限ID
            
        返回:
            Optional[Dict]: 权限信息，如果不存在则返回None
        """
        query = "SELECT * FROM permissions WHERE permission_id = ?"
        result = self.db.execute_query(query, (permission_id,))
        
        if result:
            return result[0]
        
        return None
    
    def get_permission_by_name(self, name: str) -> Optional[Dict]:
        """
        根据权限名称获取权限
        
        参数:
            name: 权限名称
            
        返回:
            Optional[Dict]: 权限信息，如果不存在则返回None
        """
        query = "SELECT * FROM permissions WHERE name = ?"
        result = self.db.execute_query(query, (name,))
        
        if result:
            return result[0]
        
        return None
    
    def update_permission(self, permission_id: str, **kwargs) -> bool:
        """
        更新权限信息
        
        参数:
            permission_id: 权限ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'description']:
                set_clause.append(f"{key} = ?")
                params.append(value)
        
        if not set_clause:
            return False
        
        query = f"UPDATE permissions SET {', '.join(set_clause)} WHERE permission_id = ?"
        params.append(permission_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新权限失败: {str(e)}")
            return False
    
    def delete_permission(self, permission_id: str) -> bool:
        """
        删除权限
        
        参数:
            permission_id: 权限ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM permissions WHERE permission_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (permission_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除权限失败: {str(e)}")
            return False
    
    def list_permissions(self) -> List[Dict]:
        """
        列出所有权限
        
        返回:
            List[Dict]: 权限信息列表
        """
        query = "SELECT * FROM permissions"
        return self.db.execute_query(query)


class SessionRepository:
    """会话数据仓库，处理会话相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化会话数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_session(self, session_id: str, user_id: str, created_at: str = None,
                      expires_at: str = None, ip_address: str = None, user_agent: str = None) -> bool:
        """
        创建新会话
        
        参数:
            session_id: 会话ID
            user_id: 用户ID
            created_at: 创建时间，如果不提供则使用当前时间
            expires_at: 过期时间，如果不提供则使用当前时间加24小时
            ip_address: IP地址
            user_agent: 用户代理
            
        返回:
            bool: 是否创建成功
        """
        if not created_at:
            created_at = datetime.datetime.now().isoformat()
        
        if not expires_at:
            expires_at = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
        
        query = '''
        INSERT INTO sessions (session_id, user_id, created_at, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                session_id, user_id, created_at, expires_at, ip_address, user_agent
            ))
            return True
        except Exception as e:
            print(f"创建会话失败: {str(e)}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        获取会话
        
        参数:
            session_id: 会话ID
            
        返回:
            Optional[Dict]: 会话信息，如果不存在则返回None
        """
        query = "SELECT * FROM sessions WHERE session_id = ?"
        result = self.db.execute_query(query, (session_id,))
        
        if result:
            return result[0]
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        参数:
            session_id: 会话ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM sessions WHERE session_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (session_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除会话失败: {str(e)}")
            return False
    
    def delete_expired_sessions(self) -> int:
        """
        删除过期会话
        
        返回:
            int: 删除的会话数量
        """
        now = datetime.datetime.now().isoformat()
        query = "DELETE FROM sessions WHERE expires_at < ?"
        
        try:
            affected_rows = self.db.execute_update(query, (now,))
            return affected_rows
        except Exception as e:
            print(f"删除过期会话失败: {str(e)}")
            return 0
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """
        获取用户的所有会话
        
        参数:
            user_id: 用户ID
            
        返回:
            List[Dict]: 会话信息列表
        """
        query = "SELECT * FROM sessions WHERE user_id = ?"
        return self.db.execute_query(query, (user_id,))
    
    def delete_user_sessions(self, user_id: str) -> int:
        """
        删除用户的所有会话
        
        参数:
            user_id: 用户ID
            
        返回:
            int: 删除的会话数量
        """
        query = "DELETE FROM sessions WHERE user_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (user_id,))
            return affected_rows
        except Exception as e:
            print(f"删除用户会话失败: {str(e)}")
            return 0


class StorageSystemRepository:
    """存储系统数据仓库，处理存储系统相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化存储系统数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_storage_system(self, system_id: str, name: str, description: str,
                             disk_space: float, token_count: int, created_by: str,
                             created_at: str = None, updated_at: str = None) -> bool:
        """
        创建新存储系统
        
        参数:
            system_id: 系统ID
            name: 系统名称
            description: 系统描述
            disk_space: 硬盘空间
            token_count: 令牌数
            created_by: 创建者用户ID
            created_at: 创建时间，如果不提供则使用当前时间
            updated_at: 更新时间，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not created_at:
            created_at = datetime.datetime.now().isoformat()
        
        if not updated_at:
            updated_at = created_at
        
        query = '''
        INSERT INTO storage_systems (system_id, name, description, disk_space, token_count,
                                   created_at, updated_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                system_id, name, description, disk_space, token_count,
                created_at, updated_at, created_by
            ))
            return True
        except Exception as e:
            print(f"创建存储系统失败: {str(e)}")
            return False
    
    def get_storage_system(self, system_id: str) -> Optional[Dict]:
        """
        获取存储系统
        
        参数:
            system_id: 系统ID
            
        返回:
            Optional[Dict]: 存储系统信息，如果不存在则返回None
        """
        query = "SELECT * FROM storage_systems WHERE system_id = ?"
        result = self.db.execute_query(query, (system_id,))
        
        if result:
            return result[0]
        
        return None
    
    def update_storage_system(self, system_id: str, **kwargs) -> bool:
        """
        更新存储系统信息
        
        参数:
            system_id: 系统ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'description', 'disk_space', 'token_count']:
                set_clause.append(f"{key} = ?")
                params.append(value)
        
        # 添加更新时间
        set_clause.append("updated_at = ?")
        params.append(datetime.datetime.now().isoformat())
        
        if not set_clause:
            return False
        
        query = f"UPDATE storage_systems SET {', '.join(set_clause)} WHERE system_id = ?"
        params.append(system_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新存储系统失败: {str(e)}")
            return False
    
    def delete_storage_system(self, system_id: str) -> bool:
        """
        删除存储系统
        
        参数:
            system_id: 系统ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM storage_systems WHERE system_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (system_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除存储系统失败: {str(e)}")
            return False
    
    def list_storage_systems(self) -> List[Dict]:
        """
        列出所有存储系统
        
        返回:
            List[Dict]: 存储系统信息列表
        """
        query = "SELECT * FROM storage_systems"
        return self.db.execute_query(query)
    
    def get_user_storage_systems(self, user_id: str) -> List[Dict]:
        """
        获取用户创建的存储系统
        
        参数:
            user_id: 用户ID
            
        返回:
            List[Dict]: 存储系统信息列表
        """
        query = "SELECT * FROM storage_systems WHERE created_by = ?"
        return self.db.execute_query(query, (user_id,))


class StorageObjectRepository:
    """存储对象数据仓库，处理存储对象相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化存储对象数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_storage_object(self, object_id: str, system_id: str, name: str,
                             size: float, access_frequency: float,
                             original_position: int, current_position: int,
                             created_at: str = None, updated_at: str = None) -> bool:
        """
        创建新存储对象
        
        参数:
            object_id: 对象ID
            system_id: 系统ID
            name: 对象名称
            size: 对象大小
            access_frequency: 访问频率
            original_position: 原始位置
            current_position: 当前位置
            created_at: 创建时间，如果不提供则使用当前时间
            updated_at: 更新时间，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not created_at:
            created_at = datetime.datetime.now().isoformat()
        
        if not updated_at:
            updated_at = created_at
        
        query = '''
        INSERT INTO storage_objects (object_id, system_id, name, size, access_frequency,
                                   original_position, current_position, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                object_id, system_id, name, size, access_frequency,
                original_position, current_position, created_at, updated_at
            ))
            return True
        except Exception as e:
            print(f"创建存储对象失败: {str(e)}")
            return False
    
    def get_storage_object(self, object_id: str) -> Optional[Dict]:
        """
        获取存储对象
        
        参数:
            object_id: 对象ID
            
        返回:
            Optional[Dict]: 存储对象信息，如果不存在则返回None
        """
        query = "SELECT * FROM storage_objects WHERE object_id = ?"
        result = self.db.execute_query(query, (object_id,))
        
        if result:
            return result[0]
        
        return None
    
    def update_storage_object(self, object_id: str, **kwargs) -> bool:
        """
        更新存储对象信息
        
        参数:
            object_id: 对象ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'size', 'access_frequency', 'current_position']:
                set_clause.append(f"{key} = ?")
                params.append(value)
        
        # 添加更新时间
        set_clause.append("updated_at = ?")
        params.append(datetime.datetime.now().isoformat())
        
        if not set_clause:
            return False
        
        query = f"UPDATE storage_objects SET {', '.join(set_clause)} WHERE object_id = ?"
        params.append(object_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新存储对象失败: {str(e)}")
            return False
    
    def delete_storage_object(self, object_id: str) -> bool:
        """
        删除存储对象
        
        参数:
            object_id: 对象ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM storage_objects WHERE object_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (object_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除存储对象失败: {str(e)}")
            return False
    
    def get_system_objects(self, system_id: str) -> List[Dict]:
        """
        获取存储系统的所有对象
        
        参数:
            system_id: 系统ID
            
        返回:
            List[Dict]: 存储对象信息列表
        """
        query = "SELECT * FROM storage_objects WHERE system_id = ? ORDER BY current_position"
        return self.db.execute_query(query, (system_id,))
    
    def batch_update_positions(self, object_positions: List[Tuple[str, int]]) -> bool:
        """
        批量更新对象位置
        
        参数:
            object_positions: 对象位置列表，每个元素为(object_id, position)元组
            
        返回:
            bool: 是否更新成功
        """
        now = datetime.datetime.now().isoformat()
        queries = []
        
        for object_id, position in object_positions:
            query = "UPDATE storage_objects SET current_position = ?, updated_at = ? WHERE object_id = ?"
            params = (position, now, object_id)
            queries.append((query, params))
        
        return self.db.execute_transaction(queries)


class OptimizationJobRepository:
    """优化任务数据仓库，处理优化任务相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化优化任务数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_job(self, job_id: str, system_id: str, algorithm: str,
                  created_by: str, started_at: str = None) -> bool:
        """
        创建新优化任务
        
        参数:
            job_id: 任务ID
            system_id: 系统ID
            algorithm: 算法名称
            created_by: 创建者用户ID
            started_at: 开始时间，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not started_at:
            started_at = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO optimization_jobs (job_id, system_id, algorithm, status, started_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                job_id, system_id, algorithm, "running", started_at, created_by
            ))
            return True
        except Exception as e:
            print(f"创建优化任务失败: {str(e)}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        获取优化任务
        
        参数:
            job_id: 任务ID
            
        返回:
            Optional[Dict]: 优化任务信息，如果不存在则返回None
        """
        query = "SELECT * FROM optimization_jobs WHERE job_id = ?"
        result = self.db.execute_query(query, (job_id,))
        
        if result:
            return result[0]
        
        return None
    
    def update_job_status(self, job_id: str, status: str) -> bool:
        """
        更新优化任务状态
        
        参数:
            job_id: 任务ID
            status: 任务状态
            
        返回:
            bool: 是否更新成功
        """
        query = "UPDATE optimization_jobs SET status = ? WHERE job_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (status, job_id))
            return affected_rows > 0
        except Exception as e:
            print(f"更新优化任务状态失败: {str(e)}")
            return False
    
    def complete_job(self, job_id: str, before_fragmentation: float, after_fragmentation: float,
                    before_score: float, after_score: float, improvement: float,
                    time_cost: float) -> bool:
        """
        完成优化任务
        
        参数:
            job_id: 任务ID
            before_fragmentation: 优化前碎片率
            after_fragmentation: 优化后碎片率
            before_score: 优化前性能得分
            after_score: 优化后性能得分
            improvement: 性能提升百分比
            time_cost: 优化耗时
            
        返回:
            bool: 是否更新成功
        """
        completed_at = datetime.datetime.now().isoformat()
        
        query = '''
        UPDATE optimization_jobs SET
            status = ?,
            before_fragmentation = ?,
            after_fragmentation = ?,
            before_score = ?,
            after_score = ?,
            improvement = ?,
            time_cost = ?,
            completed_at = ?
        WHERE job_id = ?
        '''
        
        try:
            affected_rows = self.db.execute_update(query, (
                "completed", before_fragmentation, after_fragmentation,
                before_score, after_score, improvement, time_cost,
                completed_at, job_id
            ))
            return affected_rows > 0
        except Exception as e:
            print(f"完成优化任务失败: {str(e)}")
            return False
    
    def fail_job(self, job_id: str, error_message: str) -> bool:
        """
        标记优化任务为失败
        
        参数:
            job_id: 任务ID
            error_message: 错误信息
            
        返回:
            bool: 是否更新成功
        """
        completed_at = datetime.datetime.now().isoformat()
        
        # 将错误信息存储在性能指标表中
        metric_id = str(uuid.uuid4())
        job = self.get_job(job_id)
        
        if not job:
            return False
        
        # 创建事务
        queries = [
            (
                "UPDATE optimization_jobs SET status = ?, completed_at = ? WHERE job_id = ?",
                ("failed", completed_at, job_id)
            ),
            (
                '''
                INSERT INTO performance_metrics (metric_id, system_id, job_id, metric_name, metric_value, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (metric_id, job["system_id"], job_id, "error_message", 0, completed_at)
            )
        ]
        
        return self.db.execute_transaction(queries)
    
    def get_system_jobs(self, system_id: str) -> List[Dict]:
        """
        获取存储系统的所有优化任务
        
        参数:
            system_id: 系统ID
            
        返回:
            List[Dict]: 优化任务信息列表
        """
        query = "SELECT * FROM optimization_jobs WHERE system_id = ? ORDER BY started_at DESC"
        return self.db.execute_query(query, (system_id,))
    
    def get_user_jobs(self, user_id: str) -> List[Dict]:
        """
        获取用户创建的所有优化任务
        
        参数:
            user_id: 用户ID
            
        返回:
            List[Dict]: 优化任务信息列表
        """
        query = "SELECT * FROM optimization_jobs WHERE created_by = ? ORDER BY started_at DESC"
        return self.db.execute_query(query, (user_id,))
    
    def list_jobs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        列出优化任务
        
        参数:
            limit: 返回的最大任务数
            offset: 偏移量
            
        返回:
            List[Dict]: 优化任务信息列表
        """
        query = "SELECT * FROM optimization_jobs ORDER BY started_at DESC LIMIT ? OFFSET ?"
        return self.db.execute_query(query, (limit, offset))


class PerformanceMetricRepository:
    """性能指标数据仓库，处理性能指标相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化性能指标数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_metric(self, metric_id: str, system_id: str, metric_name: str,
                     metric_value: float, job_id: str = None,
                     timestamp: str = None) -> bool:
        """
        创建新性能指标
        
        参数:
            metric_id: 指标ID
            system_id: 系统ID
            metric_name: 指标名称
            metric_value: 指标值
            job_id: 任务ID，可选
            timestamp: 时间戳，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not timestamp:
            timestamp = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO performance_metrics (metric_id, system_id, job_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                metric_id, system_id, job_id, metric_name, metric_value, timestamp
            ))
            return True
        except Exception as e:
            print(f"创建性能指标失败: {str(e)}")
            return False
    
    def get_system_metrics(self, system_id: str, metric_name: str = None,
                          start_time: str = None, end_time: str = None,
                          limit: int = 100) -> List[Dict]:
        """
        获取存储系统的性能指标
        
        参数:
            system_id: 系统ID
            metric_name: 指标名称，可选
            start_time: 开始时间，可选
            end_time: 结束时间，可选
            limit: 返回的最大指标数
            
        返回:
            List[Dict]: 性能指标信息列表
        """
        query_parts = ["SELECT * FROM performance_metrics WHERE system_id = ?"]
        params = [system_id]
        
        if metric_name:
            query_parts.append("AND metric_name = ?")
            params.append(metric_name)
        
        if start_time:
            query_parts.append("AND timestamp >= ?")
            params.append(start_time)
        
        if end_time:
            query_parts.append("AND timestamp <= ?")
            params.append(end_time)
        
        query_parts.append("ORDER BY timestamp DESC LIMIT ?")
        params.append(limit)
        
        query = " ".join(query_parts)
        
        return self.db.execute_query(query, tuple(params))
    
    def get_job_metrics(self, job_id: str) -> List[Dict]:
        """
        获取优化任务的性能指标
        
        参数:
            job_id: 任务ID
            
        返回:
            List[Dict]: 性能指标信息列表
        """
        query = "SELECT * FROM performance_metrics WHERE job_id = ? ORDER BY timestamp"
        return self.db.execute_query(query, (job_id,))
    
    def get_metric_statistics(self, system_id: str, metric_name: str,
                             start_time: str = None, end_time: str = None) -> Dict:
        """
        获取性能指标统计信息
        
        参数:
            system_id: 系统ID
            metric_name: 指标名称
            start_time: 开始时间，可选
            end_time: 结束时间，可选
            
        返回:
            Dict: 统计信息，包含min, max, avg, count字段
        """
        query_parts = [
            "SELECT MIN(metric_value) as min_value, MAX(metric_value) as max_value, "
            "AVG(metric_value) as avg_value, COUNT(*) as count "
            "FROM performance_metrics WHERE system_id = ? AND metric_name = ?"
        ]
        params = [system_id, metric_name]
        
        if start_time:
            query_parts.append("AND timestamp >= ?")
            params.append(start_time)
        
        if end_time:
            query_parts.append("AND timestamp <= ?")
            params.append(end_time)
        
        query = " ".join(query_parts)
        
        result = self.db.execute_query(query, tuple(params))
        
        if result:
            return result[0]
        
        return {
            "min_value": 0,
            "max_value": 0,
            "avg_value": 0,
            "count": 0
        }


class AuditLogRepository:
    """审计日志数据仓库，处理审计日志相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化审计日志数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_log(self, log_id: str, action: str, resource_type: str,
                  user_id: str = None, resource_id: str = None,
                  details: str = None, ip_address: str = None,
                  timestamp: str = None) -> bool:
        """
        创建新审计日志
        
        参数:
            log_id: 日志ID
            action: 操作类型
            resource_type: 资源类型
            user_id: 用户ID，可选
            resource_id: 资源ID，可选
            details: 详细信息，可选
            ip_address: IP地址，可选
            timestamp: 时间戳，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not timestamp:
            timestamp = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO audit_logs (log_id, user_id, action, resource_type, resource_id, details, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                log_id, user_id, action, resource_type, resource_id, details, ip_address, timestamp
            ))
            return True
        except Exception as e:
            print(f"创建审计日志失败: {str(e)}")
            return False
    
    def get_logs(self, user_id: str = None, action: str = None,
                resource_type: str = None, resource_id: str = None,
                start_time: str = None, end_time: str = None,
                limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取审计日志
        
        参数:
            user_id: 用户ID，可选
            action: 操作类型，可选
            resource_type: 资源类型，可选
            resource_id: 资源ID，可选
            start_time: 开始时间，可选
            end_time: 结束时间，可选
            limit: 返回的最大日志数
            offset: 偏移量
            
        返回:
            List[Dict]: 审计日志信息列表
        """
        query_parts = ["SELECT * FROM audit_logs WHERE 1=1"]
        params = []
        
        if user_id:
            query_parts.append("AND user_id = ?")
            params.append(user_id)
        
        if action:
            query_parts.append("AND action = ?")
            params.append(action)
        
        if resource_type:
            query_parts.append("AND resource_type = ?")
            params.append(resource_type)
        
        if resource_id:
            query_parts.append("AND resource_id = ?")
            params.append(resource_id)
        
        if start_time:
            query_parts.append("AND timestamp >= ?")
            params.append(start_time)
        
        if end_time:
            query_parts.append("AND timestamp <= ?")
            params.append(end_time)
        
        query_parts.append("ORDER BY timestamp DESC LIMIT ? OFFSET ?")
        params.append(limit)
        params.append(offset)
        
        query = " ".join(query_parts)
        
        return self.db.execute_query(query, tuple(params))


class SystemConfigRepository:
    """系统配置数据仓库，处理系统配置相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化系统配置数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def set_config(self, config_key: str, config_value: str,
                  description: str = None, updated_by: str = None) -> bool:
        """
        设置系统配置
        
        参数:
            config_key: 配置键
            config_value: 配置值
            description: 配置描述，可选
            updated_by: 更新者用户ID，可选
            
        返回:
            bool: 是否设置成功
        """
        updated_at = datetime.datetime.now().isoformat()
        
        # 检查配置是否已存在
        existing_config = self.get_config(config_key)
        
        if existing_config:
            # 更新配置
            query = '''
            UPDATE system_config SET config_value = ?, description = ?, updated_at = ?, updated_by = ?
            WHERE config_key = ?
            '''
            
            try:
                affected_rows = self.db.execute_update(query, (
                    config_value, description, updated_at, updated_by, config_key
                ))
                return affected_rows > 0
            except Exception as e:
                print(f"更新系统配置失败: {str(e)}")
                return False
        else:
            # 创建配置
            query = '''
            INSERT INTO system_config (config_key, config_value, description, updated_at, updated_by)
            VALUES (?, ?, ?, ?, ?)
            '''
            
            try:
                self.db.execute_insert(query, (
                    config_key, config_value, description, updated_at, updated_by
                ))
                return True
            except Exception as e:
                print(f"创建系统配置失败: {str(e)}")
                return False
    
    def get_config(self, config_key: str) -> Optional[Dict]:
        """
        获取系统配置
        
        参数:
            config_key: 配置键
            
        返回:
            Optional[Dict]: 配置信息，如果不存在则返回None
        """
        query = "SELECT * FROM system_config WHERE config_key = ?"
        result = self.db.execute_query(query, (config_key,))
        
        if result:
            return result[0]
        
        return None
    
    def delete_config(self, config_key: str) -> bool:
        """
        删除系统配置
        
        参数:
            config_key: 配置键
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM system_config WHERE config_key = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (config_key,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除系统配置失败: {str(e)}")
            return False
    
    def list_configs(self) -> List[Dict]:
        """
        列出所有系统配置
        
        返回:
            List[Dict]: 配置信息列表
        """
        query = "SELECT * FROM system_config"
        return self.db.execute_query(query)


class LicenseRepository:
    """许可证数据仓库，处理许可证相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化许可证数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_license(self, license_id: str, license_key: str, license_type: str,
                      features: str, issued_to: str, issued_at: str = None,
                      expires_at: str = None, is_active: bool = True) -> bool:
        """
        创建新许可证
        
        参数:
            license_id: 许可证ID
            license_key: 许可证密钥
            license_type: 许可证类型
            features: 功能列表，JSON字符串
            issued_to: 发放对象
            issued_at: 发放时间，如果不提供则使用当前时间
            expires_at: 过期时间，可选
            is_active: 是否激活
            
        返回:
            bool: 是否创建成功
        """
        if not issued_at:
            issued_at = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO licenses (license_id, license_key, license_type, features, issued_to,
                            issued_at, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                license_id, license_key, license_type, features, issued_to,
                issued_at, expires_at, 1 if is_active else 0
            ))
            return True
        except Exception as e:
            print(f"创建许可证失败: {str(e)}")
            return False
    
    def get_license(self, license_id: str) -> Optional[Dict]:
        """
        获取许可证
        
        参数:
            license_id: 许可证ID
            
        返回:
            Optional[Dict]: 许可证信息，如果不存在则返回None
        """
        query = "SELECT * FROM licenses WHERE license_id = ?"
        result = self.db.execute_query(query, (license_id,))
        
        if result:
            return result[0]
        
        return None
    
    def get_license_by_key(self, license_key: str) -> Optional[Dict]:
        """
        根据许可证密钥获取许可证
        
        参数:
            license_key: 许可证密钥
            
        返回:
            Optional[Dict]: 许可证信息，如果不存在则返回None
        """
        query = "SELECT * FROM licenses WHERE license_key = ?"
        result = self.db.execute_query(query, (license_key,))
        
        if result:
            return result[0]
        
        return None
    
    def update_license(self, license_id: str, **kwargs) -> bool:
        """
        更新许可证信息
        
        参数:
            license_id: 许可证ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['license_key', 'license_type', 'features', 'issued_to', 'expires_at', 'is_active']:
                set_clause.append(f"{key} = ?")
                # 对布尔值进行转换
                if key == 'is_active':
                    params.append(1 if value else 0)
                else:
                    params.append(value)
        
        if not set_clause:
            return False
        
        query = f"UPDATE licenses SET {', '.join(set_clause)} WHERE license_id = ?"
        params.append(license_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新许可证失败: {str(e)}")
            return False
    
    def delete_license(self, license_id: str) -> bool:
        """
        删除许可证
        
        参数:
            license_id: 许可证ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM licenses WHERE license_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (license_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除许可证失败: {str(e)}")
            return False
    
    def list_licenses(self) -> List[Dict]:
        """
        列出所有许可证
        
        返回:
            List[Dict]: 许可证信息列表
        """
        query = "SELECT * FROM licenses"
        return self.db.execute_query(query)
    
    def check_license_validity(self, license_key: str) -> Dict:
        """
        检查许可证有效性
        
        参数:
            license_key: 许可证密钥
            
        返回:
            Dict: 检查结果，包含is_valid, message, features字段
        """
        license_info = self.get_license_by_key(license_key)
        
        if not license_info:
            return {
                "is_valid": False,
                "message": "许可证不存在",
                "features": []
            }
        
        # 检查是否激活
        if not license_info["is_active"]:
            return {
                "is_valid": False,
                "message": "许可证未激活",
                "features": []
            }
        
        # 检查是否过期
        if license_info["expires_at"]:
            expires_at = datetime.datetime.fromisoformat(license_info["expires_at"])
            if expires_at < datetime.datetime.now():
                return {
                    "is_valid": False,
                    "message": "许可证已过期",
                    "features": []
                }
        
        # 解析功能列表
        try:
            features = json.loads(license_info["features"])
        except:
            features = []
        
        return {
            "is_valid": True,
            "message": "许可证有效",
            "features": features,
            "license_type": license_info["license_type"],
            "issued_to": license_info["issued_to"],
            "issued_at": license_info["issued_at"],
            "expires_at": license_info["expires_at"]
        }


class ScheduledTaskRepository:
    """计划任务数据仓库，处理计划任务相关的数据库操作"""
    
    def __init__(self, db: Database):
        """
        初始化计划任务数据仓库
        
        参数:
            db: 数据库管理器实例
        """
        self.db = db
    
    def create_task(self, task_id: str, name: str, task_type: str,
                   schedule: str, created_by: str, parameters: str = None,
                   is_active: bool = True, created_at: str = None) -> bool:
        """
        创建新计划任务
        
        参数:
            task_id: 任务ID
            name: 任务名称
            task_type: 任务类型
            schedule: 调度表达式
            created_by: 创建者用户ID
            parameters: 任务参数，JSON字符串
            is_active: 是否激活
            created_at: 创建时间，如果不提供则使用当前时间
            
        返回:
            bool: 是否创建成功
        """
        if not created_at:
            created_at = datetime.datetime.now().isoformat()
        
        query = '''
        INSERT INTO scheduled_tasks (task_id, name, task_type, parameters, schedule,
                                   is_active, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        try:
            self.db.execute_insert(query, (
                task_id, name, task_type, parameters, schedule,
                1 if is_active else 0, created_at, created_by
            ))
            return True
        except Exception as e:
            print(f"创建计划任务失败: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取计划任务
        
        参数:
            task_id: 任务ID
            
        返回:
            Optional[Dict]: 计划任务信息，如果不存在则返回None
        """
        query = "SELECT * FROM scheduled_tasks WHERE task_id = ?"
        result = self.db.execute_query(query, (task_id,))
        
        if result:
            return result[0]
        
        return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """
        更新计划任务信息
        
        参数:
            task_id: 任务ID
            **kwargs: 要更新的字段和值
            
        返回:
            bool: 是否更新成功
        """
        # 构建更新语句
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'task_type', 'parameters', 'schedule', 'is_active', 'last_run', 'next_run']:
                set_clause.append(f"{key} = ?")
                # 对布尔值进行转换
                if key == 'is_active':
                    params.append(1 if value else 0)
                else:
                    params.append(value)
        
        if not set_clause:
            return False
        
        query = f"UPDATE scheduled_tasks SET {', '.join(set_clause)} WHERE task_id = ?"
        params.append(task_id)
        
        try:
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
        except Exception as e:
            print(f"更新计划任务失败: {str(e)}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除计划任务
        
        参数:
            task_id: 任务ID
            
        返回:
            bool: 是否删除成功
        """
        query = "DELETE FROM scheduled_tasks WHERE task_id = ?"
        
        try:
            affected_rows = self.db.execute_update(query, (task_id,))
            return affected_rows > 0
        except Exception as e:
            print(f"删除计划任务失败: {str(e)}")
            return False
    
    def list_tasks(self, is_active: bool = None) -> List[Dict]:
        """
        列出计划任务
        
        参数:
            is_active: 是否只列出激活的任务，可选
            
        返回:
            List[Dict]: 计划任务信息列表
        """
        if is_active is not None:
            query = "SELECT * FROM scheduled_tasks WHERE is_active = ?"
            return self.db.execute_query(query, (1 if is_active else 0,))
        else:
            query = "SELECT * FROM scheduled_tasks"
            return self.db.execute_query(query)
    
    def update_task_execution(self, task_id: str, last_run: str, next_run: str = None) -> bool:
        """
        更新任务执行信息
        
        参数:
            task_id: 任务ID
            last_run: 上次执行时间
            next_run: 下次执行时间，可选
            
        返回:
            bool: 是否更新成功
        """
        if next_run:
            query = "UPDATE scheduled_tasks SET last_run = ?, next_run = ? WHERE task_id = ?"
            params = (last_run, next_run, task_id)
        else:
            query = "UPDATE scheduled_tasks SET last_run = ? WHERE task_id = ?"
            params = (last_run, task_id)
        
        try:
            affected_rows = self.db.execute_update(query, params)
            return affected_rows > 0
        except Exception as e:
            print(f"更新任务执行信息失败: {str(e)}")
            return False
    
    def get_due_tasks(self) -> List[Dict]:
        """
        获取到期的任务
        
        返回:
            List[Dict]: 到期任务信息列表
        """
        now = datetime.datetime.now().isoformat()
        
        query = '''
        SELECT * FROM scheduled_tasks
        WHERE is_active = 1 AND (next_run IS NULL OR next_run <= ?)
        '''
        
        return self.db.execute_query(query, (now,))


# 测试代码
if __name__ == "__main__":
    # 创建数据库管理器
    db = Database("test_storage_system.db")
    
    # 创建用户仓库
    user_repo = UserRepository(db)
    
    # 创建测试用户
    user_id = str(uuid.uuid4())
    user_repo.create_user(
        user_id=user_id,
        username="testuser",
        email="test@example.com",
        password_hash="password_hash",
        full_name="Test User"
    )
    
    # 获取用户
    user = user_repo.get_user_by_username("testuser")
    print(f"创建的用户: {user}")
    
    # 创建角色仓库
    role_repo = RoleRepository(db)
    
    # 创建测试角色
    role_id = str(uuid.uuid4())
    role_repo.create_role(
        role_id=role_id,
        name="testrole",
        description="Test Role"
    )
    
    # 获取角色
    role = role_repo.get_role_by_name("testrole")
    print(f"创建的角色: {role}")
    
    # 为用户添加角色
    user_repo.add_user_role(user_id, role_id)
    
    # 获取用户角色
    user_roles = user_repo.get_user_roles(user_id)
    print(f"用户角色: {user_roles}")
    
    # 关闭数据库连接
    db.close_connection()
