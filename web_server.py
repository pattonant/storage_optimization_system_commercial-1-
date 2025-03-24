#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 商业版
Web界面基础框架
"""

import os
import sys
import json
import time
import uuid
import datetime
import logging
from typing import Dict, List, Optional, Union, Any
from flask import Flask, request, jsonify, g, render_template, redirect, url_for, flash, session

# 导入认证管理器
from auth_manager import AuthManager
from database import Database, UserRepository, RoleRepository, PermissionRepository, StorageSystemRepository

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("web_server")

# 创建Flask应用
app = Flask(
    __name__, 
    static_folder='static',
    template_folder='templates'
)

# 设置密钥
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key_change_in_production")

# 创建数据库连接
db = Database()

# 创建认证管理器实例
auth_manager = AuthManager()

# 创建数据仓库实例
user_repo = UserRepository(db)
role_repo = RoleRepository(db)
permission_repo = PermissionRepository(db)
storage_system_repo = StorageSystemRepository(db)

# 会话配置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)

# 上下文处理器，向所有模板提供通用数据
@app.context_processor
def inject_common_data():
    """向所有模板注入通用数据"""
    user = None
    if 'user_id' in session:
        user = user_repo.get_user_by_id(session['user_id'])
    
    return {
        'user': user,
        'app_name': '华为云存储服务控制系统',
        'app_version': '2.0.0',
        'current_year': datetime.datetime.now().year
    }

# 请求前处理
@app.before_request
def before_request():
    """在请求处理前执行"""
    # 排除静态文件和登录页面
    if request.endpoint and 'static' in request.endpoint or request.endpoint in ['login', 'logout', 'register']:
        return
    
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户
    user = user_repo.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # 将用户信息存储在g对象中
    g.user = user

# 首页
@app.route('/')
def index():
    """首页"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取用户的存储系统
    storage_systems = storage_system_repo.get_user_storage_systems(session['user_id'])
    
    # 获取最近的优化任务
    # TODO: 实现获取最近优化任务的功能
    
    return render_template(
        'index.html',
        storage_systems=storage_systems,
        page_title='控制面板'
    )

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('login.html')
        
        # 尝试登录
        session_id = auth_manager.login(username, password)
        if not session_id:
            flash('用户名或密码错误', 'error')
            return render_template('login.html')
        
        # 获取用户信息
        user = auth_manager.get_user_from_session(session_id)
        
        # 将用户ID存储在会话中
        session['user_id'] = user.user_id
        session['username'] = user.username
        session.permanent = True
        
        # 记录登录时间
        user_repo.update_user(user.user_id, last_login=datetime.datetime.now().isoformat())
        
        # 记录登录日志
        # TODO: 实现记录登录日志的功能
        
        return redirect(url_for('index'))
    
    return render_template('login.html', page_title='登录')

# 注销
@app.route('/logout')
def logout():
    """注销"""
    session.clear()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('login'))

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('用户名、电子邮件和密码不能为空', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        # 检查用户名是否已存在
        if user_repo.get_user_by_username(username):
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        # 检查电子邮件是否已存在
        if user_repo.get_user_by_email(email):
            flash('电子邮件已存在', 'error')
            return render_template('register.html')
        
        # 创建用户
        user_id = str(uuid.uuid4())
        password_hash = auth_manager.hash_password(password)
        
        success = user_repo.create_user(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        
        if not success:
            flash('注册失败，请稍后再试', 'error')
            return render_template('register.html')
        
        # 为用户添加默认角色
        default_role = role_repo.get_role_by_name('user')
        if default_role:
            user_repo.add_user_role(user_id, default_role['role_id'])
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', page_title='注册')

# 用户个人资料
@app.route('/profile')
def profile():
    """用户个人资料"""
    return render_template('profile.html', page_title='个人资料')

# 更新个人资料
@app.route('/profile/update', methods=['POST'])
def update_profile():
    """更新个人资料"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # 获取当前用户
    user = user_repo.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # 更新字段
    update_fields = {}
    
    if full_name and full_name != user['full_name']:
        update_fields['full_name'] = full_name
    
    if email and email != user['email']:
        # 检查电子邮件是否已存在
        if user_repo.get_user_by_email(email):
            flash('电子邮件已存在', 'error')
            return redirect(url_for('profile'))
        
        update_fields['email'] = email
    
    # 如果提供了当前密码，则更新密码
    if current_password:
        # 验证当前密码
        if not auth_manager.verify_password(current_password, user['password_hash']):
            flash('当前密码错误', 'error')
            return redirect(url_for('profile'))
        
        if not new_password:
            flash('新密码不能为空', 'error')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'error')
            return redirect(url_for('profile'))
        
        # 更新密码
        update_fields['password_hash'] = auth_manager.hash_password(new_password)
    
    # 如果有字段需要更新
    if update_fields:
        success = user_repo.update_user(session['user_id'], **update_fields)
        
        if not success:
            flash('更新个人资料失败', 'error')
        else:
            flash('个人资料已更新', 'success')
    
    return redirect(url_for('profile'))

# 存储系统列表
@app.route('/storage-systems')
def storage_systems():
    """存储系统列表"""
    # 获取用户的存储系统
    systems = storage_system_repo.get_user_storage_systems(session['user_id'])
    
    return render_template(
        'storage_systems.html',
        systems=systems,
        page_title='存储系统'
    )

# 创建存储系统
@app.route('/storage-systems/create', methods=['GET', 'POST'])
def create_storage_system():
    """创建存储系统"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        disk_space = request.form.get('disk_space')
        token_count = request.form.get('token_count')
        
        if not name or not disk_space or not token_count:
            flash('名称、硬盘空间和令牌数不能为空', 'error')
            return render_template('create_storage_system.html')
        
        try:
            disk_space = float(disk_space)
            token_count = int(token_count)
        except ValueError:
            flash('硬盘空间和令牌数必须是数字', 'error')
            return render_template('create_storage_system.html')
        
        # 创建存储系统
        system_id = str(uuid.uuid4())
        
        success = storage_system_repo.create_storage_system(
            system_id=system_id,
            name=name,
            description=description,
            disk_space=disk_space,
            token_count=token_count,
            created_by=session['user_id']
        )
        
        if not success:
            flash('创建存储系统失败', 'error')
            return render_template('create_storage_system.html')
        
        flash('存储系统已创建', 'success')
        return redirect(url_for('storage_systems'))
    
    return render_template('create_storage_system.html', page_title='创建存储系统')

# 存储系统详情
@app.route('/storage-systems/<system_id>')
def storage_system_detail(system_id):
    """存储系统详情"""
    # 获取存储系统
    system = storage_system_repo.get_storage_system(system_id)
    
    if not system:
        flash('存储系统不存在', 'error')
        return redirect(url_for('storage_systems'))
    
    # 检查权限
    if system['created_by'] != session['user_id']:
        # 检查用户是否有查看其他用户存储系统的权限
        if not auth_manager.check_permission(session['user_id'], 'storage:read'):
            flash('您没有权限查看此存储系统', 'error')
            return redirect(url_for('storage_systems'))
    
    # 获取存储对象
    # TODO: 实现获取存储对象的功能
    
    # 获取优化任务
    # TODO: 实现获取优化任务的功能
    
    return render_template(
        'storage_system_detail.html',
        system=system,
        page_title=system['name']
    )

# 编辑存储系统
@app.route('/storage-systems/<system_id>/edit', methods=['GET', 'POST'])
def edit_storage_system(system_id):
    """编辑存储系统"""
    # 获取存储系统
    system = storage_system_repo.get_storage_system(system_id)
    
    if not system:
        flash('存储系统不存在', 'error')
        return redirect(url_for('storage_systems'))
    
    # 检查权限
    if system['created_by'] != session['user_id']:
        # 检查用户是否有编辑其他用户存储系统的权限
        if not auth_manager.check_permission(session['user_id'], 'storage:update'):
            flash('您没有权限编辑此存储系统', 'error')
            return redirect(url_for('storage_systems'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        disk_space = request.form.get('disk_space')
        token_count = request.form.get('token_count')
        
        if not name or not disk_space or not token_count:
            flash('名称、硬盘空间和令牌数不能为空', 'error')
            return render_template('edit_storage_system.html', system=system)
        
        try:
            disk_space = float(disk_space)
            token_count = int(token_count)
        except ValueError:
            flash('硬盘空间和令牌数必须是数字', 'error')
            return render_template('edit_storage_system.html', system=system)
        
        # 更新存储系统
        success = storage_system_repo.update_storage_system(
            system_id=system_id,
            name=name,
            description=description,
            disk_space=disk_space,
            token_count=token_count
        )
        
        if not success:
            flash('更新存储系统失败', 'error')
            return render_template('edit_storage_system.html', system=system)
        
        flash('存储系统已更新', 'success')
        return redirect(url_for('storage_system_detail', system_id=system_id))
    
    return render_template(
        'edit_storage_system.html',
        system=system,
        page_title=f'编辑 {system["name"]}'
    )

# 删除存储系统
@app.route('/storage-systems/<system_id>/delete', methods=['POST'])
def delete_storage_system(system_id):
    """删除存储系统"""
    # 获取存储系统
    system = storage_system_repo.get_storage_system(system_id)
    
    if not system:
        flash('存储系统不存在', 'error')
        return redirect(url_for('storage_systems'))
    
    # 检查权限
    if system['created_by'] != session['user_id']:
        # 检查用户是否有删除其他用户存储系统的权限
        if not auth_manager.check_permission(session['user_id'], 'storage:delete'):
            flash('您没有权限删除此存储系统', 'error')
            return redirect(url_for('storage_systems'))
    
    # 删除存储系统
    success = storage_system_repo.delete_storage_system(system_id)
    
    if not success:
        flash('删除存储系统失败', 'error')
    else:
        flash('存储系统已删除', 'success')
    
    return redirect(url_for('storage_systems'))

# 优化存储系统
@app.route('/storage-systems/<system_id>/optimize', methods=['GET', 'POST'])
def optimize_storage_system(system_id):
    """优化存储系统"""
    # 获取存储系统
    system = storage_system_repo.get_storage_system(system_id)
    
    if not system:
        flash('存储系统不存在', 'error')
        return redirect(url_for('storage_systems'))
    
    # 检查权限
    if system['created_by'] != session['user_id']:
        # 检查用户是否有优化其他用户存储系统的权限
        if not auth_manager.check_permission(session['user_id'], 'storage:optimize'):
            flash('您没有权限优化此存储系统', 'error')
            return redirect(url_for('storage_systems'))
    
    if request.method == 'POST':
        algorithm = request.form.get('algorithm')
        
        if not algorithm:
            flash('请选择优化算法', 'error')
            return render_template('optimize_storage_system.html', system=system)
        
        # 创建优化任务
        # TODO: 实现创建优化任务的功能
        
        flash('优化任务已创建，正在后台运行', 'success')
        return redirect(url_for('storage_system_detail', system_id=system_id))
    
    return render_template(
        'optimize_storage_system.html',
        system=system,
        page_title=f'优化 {system["name"]}'
    )

# 用户管理（仅管理员可见）
@app.route('/admin/users')
def admin_users():
    """用户管理"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'user:read'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # 获取所有用户
    users = user_repo.list_users()
    
    return render_template(
        'admin/users.html',
        users=users,
        page_title='用户管理'
    )

# 创建用户（仅管理员可见）
@app.route('/admin/users/create', methods=['GET', 'POST'])
def admin_create_user():
    """创建用户"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'user:create'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        roles = request.form.getlist('roles')
        is_active = request.form.get('is_active') == 'on'
        
        if not username or not email or not password:
            flash('用户名、电子邮件和密码不能为空', 'error')
            return render_template('admin/create_user.html')
        
        # 检查用户名是否已存在
        if user_repo.get_user_by_username(username):
            flash('用户名已存在', 'error')
            return render_template('admin/create_user.html')
        
        # 检查电子邮件是否已存在
        if user_repo.get_user_by_email(email):
            flash('电子邮件已存在', 'error')
            return render_template('admin/create_user.html')
        
        # 创建用户
        user_id = str(uuid.uuid4())
        password_hash = auth_manager.hash_password(password)
        
        success = user_repo.create_user(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            is_active=is_active
        )
        
        if not success:
            flash('创建用户失败', 'error')
            return render_template('admin/create_user.html')
        
        # 为用户添加角色
        for role_name in roles:
            role = role_repo.get_role_by_name(role_name)
            if role:
                user_repo.add_user_role(user_id, role['role_id'])
        
        flash('用户已创建', 'success')
        return redirect(url_for('admin_users'))
    
    # 获取所有角色
    roles = role_repo.list_roles()
    
    return render_template(
        'admin/create_user.html',
        roles=roles,
        page_title='创建用户'
    )

# 编辑用户（仅管理员可见）
@app.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    """编辑用户"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'user:update'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # 获取用户
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        roles = request.form.getlist('roles')
        is_active = request.form.get('is_active') == 'on'
        password = request.form.get('password')
        
        # 更新字段
        update_fields = {}
        
        if email and email != user['email']:
            # 检查电子邮件是否已存在
            existing_user = user_repo.get_user_by_email(email)
            if existing_user and existing_user['user_id'] != user_id:
                flash('电子邮件已存在', 'error')
                return redirect(url_for('admin_edit_user', user_id=user_id))
            
            update_fields['email'] = email
        
        if full_name != user['full_name']:
            update_fields['full_name'] = full_name
        
        if is_active != bool(user['is_active']):
            update_fields['is_active'] = is_active
        
        # 如果提供了密码，则更新密码
        if password:
            update_fields['password_hash'] = auth_manager.hash_password(password)
        
        # 如果有字段需要更新
        if update_fields:
            success = user_repo.update_user(user_id, **update_fields)
            
            if not success:
                flash('更新用户失败', 'error')
                return redirect(url_for('admin_edit_user', user_id=user_id))
        
        # 更新角色
        # 获取用户当前角色
        current_roles = user_repo.get_user_roles(user_id)
        current_role_ids = [role['role_id'] for role in current_roles]
        
        # 获取新角色
        new_roles = []
        for role_name in roles:
            role = role_repo.get_role_by_name(role_name)
            if role:
                new_roles.append(role)
        
        new_role_ids = [role['role_id'] for role in new_roles]
        
        # 删除不再需要的角色
        for role_id in current_role_ids:
            if role_id not in new_role_ids:
                user_repo.remove_user_role(user_id, role_id)
        
        # 添加新角色
        for role_id in new_role_ids:
            if role_id not in current_role_ids:
                user_repo.add_user_role(user_id, role_id)
        
        flash('用户已更新', 'success')
        return redirect(url_for('admin_users'))
    
    # 获取用户角色
    user_roles = user_repo.get_user_roles(user_id)
    user_role_names = [role['name'] for role in user_roles]
    
    # 获取所有角色
    roles = role_repo.list_roles()
    
    return render_template(
        'admin/edit_user.html',
        user=user,
        roles=roles,
        user_role_names=user_role_names,
        page_title=f'编辑用户 {user["username"]}'
    )

# 删除用户（仅管理员可见）
@app.route('/admin/users/<user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """删除用户"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'user:delete'):
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('admin_users'))
    
    # 不能删除自己
    if user_id == session['user_id']:
        flash('不能删除当前登录的用户', 'error')
        return redirect(url_for('admin_users'))
    
    # 获取用户
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('admin_users'))
    
    # 删除用户
    success = user_repo.delete_user(user_id)
    
    if not success:
        flash('删除用户失败', 'error')
    else:
        flash('用户已删除', 'success')
    
    return redirect(url_for('admin_users'))

# 角色管理（仅管理员可见）
@app.route('/admin/roles')
def admin_roles():
    """角色管理"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'role:read'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # 获取所有角色
    roles = role_repo.list_roles()
    
    return render_template(
        'admin/roles.html',
        roles=roles,
        page_title='角色管理'
    )

# 创建角色（仅管理员可见）
@app.route('/admin/roles/create', methods=['GET', 'POST'])
def admin_create_role():
    """创建角色"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'role:create'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        permissions = request.form.getlist('permissions')
        
        if not name:
            flash('角色名称不能为空', 'error')
            return render_template('admin/create_role.html')
        
        # 检查角色名称是否已存在
        if role_repo.get_role_by_name(name):
            flash('角色名称已存在', 'error')
            return render_template('admin/create_role.html')
        
        # 创建角色
        role_id = str(uuid.uuid4())
        
        success = role_repo.create_role(
            role_id=role_id,
            name=name,
            description=description
        )
        
        if not success:
            flash('创建角色失败', 'error')
            return render_template('admin/create_role.html')
        
        # 为角色添加权限
        for permission_name in permissions:
            permission = permission_repo.get_permission_by_name(permission_name)
            if permission:
                role_repo.add_role_permission(role_id, permission['permission_id'])
        
        flash('角色已创建', 'success')
        return redirect(url_for('admin_roles'))
    
    # 获取所有权限
    permissions = permission_repo.list_permissions()
    
    return render_template(
        'admin/create_role.html',
        permissions=permissions,
        page_title='创建角色'
    )

# 编辑角色（仅管理员可见）
@app.route('/admin/roles/<role_id>/edit', methods=['GET', 'POST'])
def admin_edit_role(role_id):
    """编辑角色"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'role:update'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # 获取角色
    role = role_repo.get_role_by_id(role_id)
    
    if not role:
        flash('角色不存在', 'error')
        return redirect(url_for('admin_roles'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        permissions = request.form.getlist('permissions')
        
        # 更新角色
        success = role_repo.update_role(
            role_id=role_id,
            description=description
        )
        
        if not success:
            flash('更新角色失败', 'error')
            return redirect(url_for('admin_edit_role', role_id=role_id))
        
        # 更新权限
        # 获取角色当前权限
        current_permissions = role_repo.get_role_permissions(role_id)
        current_permission_ids = [perm['permission_id'] for perm in current_permissions]
        
        # 获取新权限
        new_permissions = []
        for permission_name in permissions:
            permission = permission_repo.get_permission_by_name(permission_name)
            if permission:
                new_permissions.append(permission)
        
        new_permission_ids = [perm['permission_id'] for perm in new_permissions]
        
        # 删除不再需要的权限
        for permission_id in current_permission_ids:
            if permission_id not in new_permission_ids:
                role_repo.remove_role_permission(role_id, permission_id)
        
        # 添加新权限
        for permission_id in new_permission_ids:
            if permission_id not in current_permission_ids:
                role_repo.add_role_permission(role_id, permission_id)
        
        flash('角色已更新', 'success')
        return redirect(url_for('admin_roles'))
    
    # 获取角色权限
    role_permissions = role_repo.get_role_permissions(role_id)
    role_permission_names = [perm['name'] for perm in role_permissions]
    
    # 获取所有权限
    permissions = permission_repo.list_permissions()
    
    return render_template(
        'admin/edit_role.html',
        role=role,
        permissions=permissions,
        role_permission_names=role_permission_names,
        page_title=f'编辑角色 {role["name"]}'
    )

# 删除角色（仅管理员可见）
@app.route('/admin/roles/<role_id>/delete', methods=['POST'])
def admin_delete_role(role_id):
    """删除角色"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'role:delete'):
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('admin_roles'))
    
    # 获取角色
    role = role_repo.get_role_by_id(role_id)
    
    if not role:
        flash('角色不存在', 'error')
        return redirect(url_for('admin_roles'))
    
    # 不能删除admin角色
    if role['name'] == 'admin':
        flash('不能删除admin角色', 'error')
        return redirect(url_for('admin_roles'))
    
    # 删除角色
    success = role_repo.delete_role(role_id)
    
    if not success:
        flash('删除角色失败', 'error')
    else:
        flash('角色已删除', 'success')
    
    return redirect(url_for('admin_roles'))

# 系统设置（仅管理员可见）
@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """系统设置"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'system:manage'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # TODO: 实现系统设置功能
    
    return render_template(
        'admin/settings.html',
        page_title='系统设置'
    )

# 系统监控（仅管理员可见）
@app.route('/admin/monitor')
def admin_monitor():
    """系统监控"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'system:monitor'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # TODO: 实现系统监控功能
    
    return render_template(
        'admin/monitor.html',
        page_title='系统监控'
    )

# 许可证管理（仅管理员可见）
@app.route('/admin/license', methods=['GET', 'POST'])
def admin_license():
    """许可证管理"""
    # 检查权限
    if not auth_manager.check_permission(session['user_id'], 'system:manage'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # TODO: 实现许可证管理功能
    
    return render_template(
        'admin/license.html',
        page_title='许可证管理'
    )

# 帮助页面
@app.route('/help')
def help_page():
    """帮助页面"""
    return render_template('help.html', page_title='帮助')

# 关于页面
@app.route('/about')
def about_page():
    """关于页面"""
    return render_template('about.html', page_title='关于')

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    """404错误页面"""
    return render_template('errors/404.html', page_title='页面未找到'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500错误页面"""
    return render_template('errors/500.html', page_title='服务器错误'), 500

# 主函数
if __name__ == "__main__":
    # 设置主机和端口
    host = os.environ.get("WEB_HOST", "0.0.0.0")
    port = int(os.environ.get("WEB_PORT", 8080))
    
    # 设置调试模式
    debug = os.environ.get("WEB_DEBUG", "false").lower() == "true"
    
    print(f"启动Web服务器，监听地址: {host}:{port}，调试模式: {debug}")
    app.run(host=host, port=port, debug=debug)
