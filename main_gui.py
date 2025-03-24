#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 现代化GUI界面
主要功能：通过减少硬盘数据碎片化程度，提升系统整体效率
"""

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# 导入优化器模块
from optimizer import StorageOptimizer

# 设置主题颜色
COLORS = {
    "primary": "#1976D2",  # 蓝色
    "secondary": "#03A9F4",  # 浅蓝色
    "accent": "#FF5722",  # 橙色
    "background": "#F5F5F5",  # 浅灰色
    "card": "#FFFFFF",  # 白色
    "text": "#212121",  # 深灰色
    "text_secondary": "#757575",  # 中灰色
    "border": "#EEEEEE",  # 极浅灰色
    "success": "#4CAF50",  # 绿色
    "warning": "#FFC107",  # 黄色
    "error": "#F44336",  # 红色
}

class ModernButton(ttk.Button):
    """现代化按钮"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TButton')
        ttk.Button.__init__(self, master, style=self.style_name, **kwargs)

class ModernFrame(ttk.Frame):
    """现代化框架"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TFrame')
        ttk.Frame.__init__(self, master, style=self.style_name, **kwargs)

class ModernLabel(ttk.Label):
    """现代化标签"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TLabel')
        ttk.Label.__init__(self, master, style=self.style_name, **kwargs)

class ModernEntry(ttk.Entry):
    """现代化输入框"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TEntry')
        ttk.Entry.__init__(self, master, style=self.style_name, **kwargs)

class ModernCombobox(ttk.Combobox):
    """现代化下拉框"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TCombobox')
        ttk.Combobox.__init__(self, master, style=self.style_name, **kwargs)

class ModernProgressbar(ttk.Progressbar):
    """现代化进度条"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.Horizontal.TProgressbar')
        ttk.Progressbar.__init__(self, master, style=self.style_name, **kwargs)

class ModernNotebook(ttk.Notebook):
    """现代化选项卡"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TNotebook')
        ttk.Notebook.__init__(self, master, style=self.style_name, **kwargs)

class StorageOptimizationSystemGUI:
    """华为云存储服务控制系统GUI类"""
    def __init__(self, root):
        self.root = root
        self.root.title("华为云存储服务控制系统")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["background"])
        
        # 设置样式
        self.setup_styles()
        
        # 创建主框架
        self.main_frame = ModernFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 创建标题栏
        self.create_title_bar()
        
        # 创建内容区域
        self.content_frame = ModernFrame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建选项卡
        self.notebook = ModernNotebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 数据导入选项卡
        self.import_frame = ModernFrame(self.notebook)
        self.notebook.add(self.import_frame, text="数据导入")
        self.setup_import_tab()
        
        # 系统优化选项卡
        self.optimization_frame = ModernFrame(self.notebook)
        self.notebook.add(self.optimization_frame, text="系统优化")
        self.setup_optimization_tab()
        
        # 结果分析选项卡
        self.analysis_frame = ModernFrame(self.notebook)
        self.notebook.add(self.analysis_frame, text="结果分析")
        self.setup_analysis_tab()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 数据存储
        self.input_data = None
        self.optimization_result = None
        self.optimizer = None
        self.viz_canvas = None
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 设置主题
        try:
            style.theme_use("clam")  # 使用clam主题作为基础
        except:
            pass  # 如果主题不可用，使用默认主题
        
        # 配置按钮样式
        style.configure(
            "Modern.TButton",
            background=COLORS["primary"],
            foreground="white",
            padding=(10, 5),
            font=("微软雅黑", 10),
            borderwidth=0
        )
        style.map(
            "Modern.TButton",
            background=[("active", COLORS["secondary"])],
            foreground=[("active", "white")]
        )
        
        # 配置标签样式
        style.configure(
            "Modern.TLabel",
            background=COLORS["background"],
            foreground=COLORS["text"],
            font=("微软雅黑", 10)
        )
        
        # 配置标题标签样式
        style.configure(
            "Title.TLabel",
            background=COLORS["background"],
            foreground=COLORS["primary"],
            font=("微软雅黑", 16, "bold")
        )
        
        # 配置框架样式
        style.configure(
            "Modern.TFrame",
            background=COLORS["background"]
        )
        
        # 配置卡片框架样式
        style.configure(
            "Card.TFrame",
            background=COLORS["card"],
            relief="flat",
            borderwidth=1
        )
        
        # 配置输入框样式
        style.configure(
            "Modern.TEntry",
            fieldbackground=COLORS["card"],
            borderwidth=1,
            padding=5
        )
        
        # 配置下拉框样式
        style.configure(
            "Modern.TCombobox",
            fieldbackground=COLORS["card"],
            padding=5
        )
        
        # 配置进度条样式
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=COLORS["background"],
            background=COLORS["primary"],
            thickness=10
        )
        
        # 配置选项卡样式
        style.configure(
            "Modern.TNotebook",
            background=COLORS["background"],
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background=COLORS["card"],
            foreground=COLORS["text_secondary"],
            padding=[10, 5],
            font=("微软雅黑", 10)
        )
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "white")],
            expand=[("selected", [1, 1, 1, 0])]
        )
        
        # 配置LabelFrame样式
        style.configure(
            "Card.TLabelframe",
            background=COLORS["card"],
            foreground=COLORS["text"],
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=COLORS["card"],
            foreground=COLORS["primary"],
            font=("微软雅黑", 10, "bold")
        )
    
    def create_title_bar(self):
        """创建标题栏"""
        title_frame = ModernFrame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(
            title_frame, 
            text="华为云存储服务控制系统",
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = ttk.Label(
            title_frame,
            text="v1.0",
            style="Modern.TLabel"
        )
        version_label.pack(side=tk.RIGHT)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ModernFrame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=5)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Modern.TLabel"
        )
        status_label.pack(side=tk.LEFT)
    
    def setup_import_tab(self):
        """设置数据导入选项卡"""
        # 文件选择卡片
        file_card = ttk.LabelFrame(
            self.import_frame,
            text="数据文件",
            style="Card.TLabelframe",
            padding=10
        )
        file_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 文件路径输入
        path_frame = ModernFrame(file_card)
        path_frame.pack(fill=tk.X, pady=5)
        
        path_label = ModernLabel(path_frame, text="文件路径:")
        path_label.pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        path_entry = ModernEntry(path_frame, textvariable=self.file_path_var, width=50)
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ModernButton(path_frame, text="浏览...", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # 导入按钮
        btn_frame = ModernFrame(file_card)
        btn_frame.pack(fill=tk.X, pady=10)
        
        import_btn = ModernButton(btn_frame, text="导入数据", command=self.import_data)
        import_btn.pack(side=tk.RIGHT)
        
        # 数据预览卡片
        preview_card = ttk.LabelFrame(
            self.import_frame,
            text="数据预览",
            style="Card.TLabelframe",
            padding=10
        )
        preview_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建预览文本框
        preview_frame = ModernFrame(preview_card)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        # 数据统计卡片
        stats_card = ttk.LabelFrame(
            self.import_frame,
            text="数据统计",
            style="Card.TLabelframe",
            padding=10
        )
        stats_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 创建统计信息网格
        stats_grid = ModernFrame(stats_card)
        stats_grid.pack(fill=tk.X, pady=5)
        
        # 第一行
        ModernLabel(stats_grid, text="对象数量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.object_count_var = tk.StringVar(value="0")
        ModernLabel(stats_grid, textvariable=self.object_count_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ModernLabel(stats_grid, text="总大小:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.total_size_var = tk.StringVar(value="0 GB")
        ModernLabel(stats_grid, textvariable=self.total_size_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 第二行
        ModernLabel(stats_grid, text="平均大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.avg_size_var = tk.StringVar(value="0 GB")
        ModernLabel(stats_grid, textvariable=self.avg_size_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ModernLabel(stats_grid, text="平均访问频率:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.avg_freq_var = tk.StringVar(value="0")
        ModernLabel(stats_grid, textvariable=self.avg_freq_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
    
    def setup_optimization_tab(self):
        """设置系统优化选项卡"""
        # 参数设置卡片
        params_card = ttk.LabelFrame(
            self.optimization_frame,
            text="优化参数",
            style="Card.TLabelframe",
            padding=10
        )
        params_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 参数网格
        params_grid = ModernFrame(params_card)
        params_grid.pack(fill=tk.X, pady=5)
        
        # 硬盘空间设置
        ModernLabel(params_grid, text="硬盘空间 (GB):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.disk_space_var = tk.StringVar(value="1000")
        disk_entry = ModernEntry(params_grid, textvariable=self.disk_space_var, width=10)
        disk_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 令牌数设置
        ModernLabel(params_grid, text="令牌数:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.token_count_var = tk.StringVar(value="100")
        token_entry = ModernEntry(params_grid, textvariable=self.token_count_var, width=10)
        token_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 算法选择
        ModernLabel(params_grid, text="优化算法:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.algorithm_var = tk.StringVar(value="贪心算法")
        algorithms = ["贪心算法", "动态规划", "启发式搜索"]
        algo_combo = ModernCombobox(
            params_grid,
            textvariable=self.algorithm_var,
            values=algorithms,
            state="readonly",
            width=15
        )
        algo_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 优化按钮
        btn_frame = ModernFrame(params_card)
        btn_frame.pack(fill=tk.X, pady=10)
        
        optimize_btn = ModernButton(btn_frame, text="开始优化", command=self.start_optimization)
        optimize_btn.pack(side=tk.RIGHT)
        
        # 进度卡片
        progress_card = ttk.LabelFrame(
            self.optimization_frame,
            text="优化进度",
            style="Card.TLabelframe",
            padding=10
        )
        progress_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 进度条
        progress_frame = ModernFrame(progress_card)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ModernProgressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=200
        )
        progress_bar.pack(fill=tk.X, pady=5)
        
        # 进度标签
        self.progress_label_var = tk.StringVar(value="0%")
        progress_label = ModernLabel(progress_frame, textvariable=self.progress_label_var)
        progress_label.pack(pady=5)
        
        # 日志卡片
        log_card = ttk.LabelFrame(
            self.optimization_frame,
            text="优化日志",
            style="Card.TLabelframe",
            padding=10
        )
        log_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 日志文本框
        log_frame = ModernFrame(log_card)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            height=10
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
    
    def setup_analysis_tab(self):
        """设置结果分析选项卡"""
        # 结果统计卡片
        stats_card = ttk.LabelFrame(
            self.analysis_frame,
            text="优化统计",
            style="Card.TLabelframe",
            padding=10
        )
        stats_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 创建统计信息网格
        stats_grid = ModernFrame(stats_card)
        stats_grid.pack(fill=tk.X, pady=5)
        
        # 第一行
        ModernLabel(stats_grid, text="优化前碎片率:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.before_frag_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.before_frag_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ModernLabel(stats_grid, text="优化后碎片率:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.after_frag_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.after_frag_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 第二行
        ModernLabel(stats_grid, text="优化前性能得分:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.before_score_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.before_score_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ModernLabel(stats_grid, text="优化后性能得分:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.after_score_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.after_score_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 第三行
        ModernLabel(stats_grid, text="性能提升:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.improvement_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.improvement_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ModernLabel(stats_grid, text="优化耗时:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.time_cost_var = tk.StringVar(value="N/A")
        ModernLabel(stats_grid, textvariable=self.time_cost_var).grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 结果可视化卡片
        viz_card = ttk.LabelFrame(
            self.analysis_frame,
            text="结果可视化",
            style="Card.TLabelframe",
            padding=10
        )
        viz_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 可视化选项
        viz_options_frame = ModernFrame(viz_card)
        viz_options_frame.pack(fill=tk.X, pady=5)
        
        ModernLabel(viz_options_frame, text="可视化类型:").pack(side=tk.LEFT, padx=5)
        self.viz_type_var = tk.StringVar(value="碎片分布图")
        viz_types = ["碎片分布图", "性能对比图", "对象布局图"]
        viz_combo = ModernCombobox(
            viz_options_frame,
            textvariable=self.viz_type_var,
            values=viz_types,
            state="readonly",
            width=15
        )
        viz_combo.pack(side=tk.LEFT, padx=5)
        
        viz_btn = ModernButton(viz_options_frame, text="生成图表", command=self.generate_visualization)
        viz_btn.pack(side=tk.LEFT, padx=5)
        
        # 可视化画布
        self.viz_canvas_frame = ModernFrame(viz_card)
        self.viz_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        viz_placeholder = ModernLabel(self.viz_canvas_frame, text="请先运行优化并生成图表")
        viz_placeholder.pack(expand=True)
        
        # 导出结果按钮
        export_frame = ModernFrame(self.analysis_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_result_btn = ModernButton(export_frame, text="导出结果报告", command=self.export_report)
        export_result_btn.pack(side=tk.RIGHT, padx=5)
        
        export_data_btn = ModernButton(export_frame, text="导出优化数据", command=self.export_data)
        export_data_btn.pack(side=tk.RIGHT, padx=5)
    
    def browse_file(self):
        """浏览文件对话框"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("输入文件", "*.in"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def import_data(self):
        """导入数据文件"""
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("错误", "请选择数据文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        try:
            self.status_var.set("正在导入数据...")
            self.root.update_idletasks()
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示文件内容预览
            self.preview_text.delete(1.0, tk.END)
            preview_content = content[:2000] + ("\n..." if len(content) > 2000 else "")
            self.preview_text.insert(tk.END, preview_content)
            
            # 创建优化器实例
            try:
                disk_space = float(self.disk_space_var.get())
                token_count = int(self.token_count_var.get())
            except ValueError:
                disk_space = 1000.0
                token_count = 100
                self.disk_space_var.set(str(disk_space))
                self.token_count_var.set(str(token_count))
            
            self.optimizer = StorageOptimizer(disk_space, token_count)
            
            # 加载数据
            if self.optimizer.load_data(content):
                self.input_data = content
                
                # 更新数据统计信息
                self.update_data_stats()
                
                self.status_var.set(f"成功导入数据文件: {os.path.basename(file_path)}")
                messagebox.showinfo("成功", "数据导入成功")
                
                # 切换到优化选项卡
                self.notebook.select(1)
            else:
                self.status_var.set("导入数据失败")
                messagebox.showerror("错误", "数据格式不正确或解析失败")
            
        except Exception as e:
            self.status_var.set("导入数据失败")
            messagebox.showerror("错误", f"导入数据失败: {str(e)}")
    
    def update_data_stats(self):
        """更新数据统计信息"""
        if self.optimizer and self.optimizer.objects:
            # 对象数量
            object_count = len(self.optimizer.objects)
            self.object_count_var.set(str(object_count))
            
            # 总大小
            total_size = sum(obj['size'] for obj in self.optimizer.objects)
            self.total_size_var.set(f"{total_size:.2f} GB")
            
            # 平均大小
            avg_size = total_size / object_count if object_count > 0 else 0
            self.avg_size_var.set(f"{avg_size:.2f} GB")
            
            # 平均访问频率
            avg_freq = sum(obj['access_frequency'] for obj in self.optimizer.objects) / object_count if object_count > 0 else 0
            self.avg_freq_var.set(f"{avg_freq:.4f}")
    
    def start_optimization(self):
        """开始优化处理"""
        if not self.optimizer:
            messagebox.showerror("错误", "请先导入数据")
            return
        
        try:
            disk_space = float(self.disk_space_var.get())
            token_count = int(self.token_count_var.get())
            
            # 更新优化器参数
            self.optimizer.disk_space = disk_space
            self.optimizer.token_count = token_count
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的硬盘空间和令牌数")
            return
        
        algorithm = self.algorithm_var.get()
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"开始优化...\n算法: {algorithm}\n硬盘空间: {disk_space} GB\n令牌数: {token_count}\n\n")
        
        # 重置进度条
        self.progress_var.set(0)
        self.progress_label_var.set("0%")
        
        # 在新线程中运行优化，避免阻塞UI
        threading.Thread(target=self.run_optimization, args=(algorithm,), daemon=True).start()
    
    def run_optimization(self, algorithm):
        """在后台线程中运行优化算法"""
        self.status_var.set(f"正在使用{algorithm}优化...")
        
        try:
            # 定义进度回调函数
            def progress_callback(progress):
                self.progress_var.set(progress)
                self.progress_label_var.set(f"{progress:.1f}%")
                
                # 每10%更新一次日志
                if int(progress) % 10 == 0:
                    self.append_log(f"优化进度: {progress:.1f}%\n")
                
                # 更新UI
                self.root.update_idletasks()
            
            # 运行优化
            self.optimization_result = self.optimizer.optimize(algorithm, progress_callback)
            
            # 更新结果
            self.update_results()
            
            self.append_log(f"\n优化完成！耗时: {self.optimization_result['time_cost']:.2f} 秒\n")
            self.append_log(f"优化前碎片率: {self.optimization_result['before_fragmentation']:.2f}%\n")
            self.append_log(f"优化后碎片率: {self.optimization_result['after_fragmentation']:.2f}%\n")
            self.append_log(f"性能提升: {self.optimization_result['improvement']:.2f}%\n")
            
            self.status_var.set("优化完成")
            
            # 切换到结果分析选项卡
            self.root.after(0, lambda: self.notebook.select(2))
            
        except Exception as e:
            self.append_log(f"\n优化失败: {str(e)}\n")
            self.status_var.set("优化失败")
            messagebox.showerror("错误", f"优化过程中发生错误: {str(e)}")
    
    def append_log(self, text):
        """向日志文本框添加文本"""
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_results(self):
        """更新结果统计信息"""
        if self.optimization_result:
            self.before_frag_var.set(f"{self.optimization_result['before_fragmentation']:.2f}%")
            self.after_frag_var.set(f"{self.optimization_result['after_fragmentation']:.2f}%")
            self.before_score_var.set(f"{self.optimization_result['before_score']:.2f}")
            self.after_score_var.set(f"{self.optimization_result['after_score']:.2f}")
            self.improvement_var.set(f"{self.optimization_result['improvement']:.2f}%")
            self.time_cost_var.set(f"{self.optimization_result['time_cost']:.2f} 秒")
    
    def generate_visualization(self):
        """生成可视化图表"""
        if not self.optimization_result or not self.optimizer:
            messagebox.showerror("错误", "请先运行优化")
            return
        
        viz_type = self.viz_type_var.get()
        
        # 清除现有的可视化内容
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # 创建图表
        fig = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        if viz_type == "碎片分布图":
            self.create_fragmentation_chart(ax)
        elif viz_type == "性能对比图":
            self.create_performance_chart(ax)
        elif viz_type == "对象布局图":
            self.create_layout_chart(ax)
        
        # 设置图表样式
        fig.patch.set_facecolor(COLORS["card"])
        ax.set_facecolor(COLORS["card"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(COLORS["border"])
        ax.spines['left'].set_color(COLORS["border"])
        ax.tick_params(colors=COLORS["text_secondary"])
        ax.xaxis.label.set_color(COLORS["text"])
        ax.yaxis.label.set_color(COLORS["text"])
        ax.title.set_color(COLORS["primary"])
        
        # 添加图表到画布
        canvas = FigureCanvasTkAgg(fig, master=self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 保存画布引用
        self.viz_canvas = canvas
        
        self.status_var.set(f"已生成{viz_type}")
    
    def create_fragmentation_chart(self, ax):
        """创建碎片分布图"""
        # 获取优化前后的碎片率
        before_frag = self.optimization_result['before_fragmentation']
        after_frag = self.optimization_result['after_fragmentation']
        
        # 创建条形图
        labels = ['优化前', '优化后']
        values = [before_frag, after_frag]
        colors = [COLORS["secondary"], COLORS["primary"]]
        
        bars = ax.bar(labels, values, color=colors, width=0.5)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.2f}%', ha='center', va='bottom')
        
        # 设置图表属性
        ax.set_title('优化前后碎片率对比')
        ax.set_ylabel('碎片率 (%)')
        ax.set_ylim(0, max(values) * 1.2)  # 设置y轴上限为最大值的1.2倍
        
        # 添加网格线
        ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    def create_performance_chart(self, ax):
        """创建性能对比图"""
        # 获取优化前后的性能指标
        metrics = {
            '碎片率': [self.optimization_result['before_fragmentation'], 
                     self.optimization_result['after_fragmentation']],
            '性能得分': [self.optimization_result['before_score'], 
                      self.optimization_result['after_score']]
        }
        
        # 设置x轴位置
        x = np.arange(len(metrics))
        width = 0.35
        
        # 创建分组条形图
        bars1 = ax.bar(x - width/2, [metrics[k][0] for k in metrics], width, label='优化前', color=COLORS["secondary"])
        bars2 = ax.bar(x + width/2, [metrics[k][1] for k in metrics], width, label='优化后', color=COLORS["primary"])
        
        # 添加数值标签
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.2f}', ha='center', va='bottom')
        
        add_labels(bars1)
        add_labels(bars2)
        
        # 设置图表属性
        ax.set_title('优化前后性能指标对比')
        ax.set_xticks(x)
        ax.set_xticklabels(list(metrics.keys()))
        ax.legend()
        
        # 添加网格线
        ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    def create_layout_chart(self, ax):
        """创建对象布局图"""
        if not self.optimizer.optimized_layout:
            ax.text(0.5, 0.5, '没有可用的布局数据', ha='center', va='center')
            return
        
        # 获取优化前后的对象布局
        original_layout = self.optimizer.current_layout
        optimized_layout = self.optimizer.optimized_layout
        
        # 选择前20个对象进行可视化（避免图表过于拥挤）
        limit = min(20, len(original_layout))
        
        # 准备数据
        original_positions = list(range(limit))
        optimized_positions = []
        
        # 找出优化后前20个对象在优化前的位置
        for i in range(limit):
            obj_idx = optimized_layout[i]
            orig_pos = original_layout.index(obj_idx)
            optimized_positions.append(orig_pos)
        
        # 创建散点图
        ax.scatter(original_positions, [1] * limit, s=100, color=COLORS["secondary"], label='优化前位置')
        ax.scatter(optimized_positions, [0] * limit, s=100, color=COLORS["primary"], label='优化后位置')
        
        # 绘制连接线
        for i, opt_pos in enumerate(optimized_positions):
            ax.plot([i, opt_pos], [0, 1], 'k-', alpha=0.3)
        
        # 设置图表属性
        ax.set_title('对象布局变化（前20个对象）')
        ax.set_xlabel('对象位置索引')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['优化后', '优化前'])
        ax.set_xlim(-1, limit)
        ax.legend(loc='upper right')
        
        # 移除y轴刻度线
        ax.tick_params(axis='y', which='both', left=False)
    
    def export_report(self):
        """导出结果报告"""
        if not self.optimization_result:
            messagebox.showerror("错误", "请先运行优化")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("华为云存储服务控制系统 - 优化结果报告\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write("优化参数:\n")
                    f.write(f"- 硬盘空间: {self.optimizer.disk_space} GB\n")
                    f.write(f"- 令牌数: {self.optimizer.token_count}\n")
                    f.write(f"- 优化算法: {self.optimization_result['algorithm']}\n\n")
                    
                    f.write("数据统计:\n")
                    f.write(f"- 对象数量: {len(self.optimizer.objects)}\n")
                    total_size = sum(obj['size'] for obj in self.optimizer.objects)
                    f.write(f"- 总大小: {total_size:.2f} GB\n")
                    avg_size = total_size / len(self.optimizer.objects) if self.optimizer.objects else 0
                    f.write(f"- 平均大小: {avg_size:.2f} GB\n\n")
                    
                    f.write("优化结果:\n")
                    f.write(f"- 优化前碎片率: {self.optimization_result['before_fragmentation']:.2f}%\n")
                    f.write(f"- 优化后碎片率: {self.optimization_result['after_fragmentation']:.2f}%\n")
                    f.write(f"- 优化前性能得分: {self.optimization_result['before_score']:.2f}\n")
                    f.write(f"- 优化后性能得分: {self.optimization_result['after_score']:.2f}\n")
                    f.write(f"- 性能提升: {self.optimization_result['improvement']:.2f}%\n")
                    f.write(f"- 优化耗时: {self.optimization_result['time_cost']:.2f} 秒\n\n")
                    
                    f.write("优化后的对象布局（前20个）:\n")
                    optimized_layout = self.optimizer.get_optimized_layout()
                    for i, obj in enumerate(optimized_layout[:20]):
                        f.write(f"{i+1}. ID: {obj['id']}, 大小: {obj['size']:.2f} GB, "
                                f"访问频率: {obj['access_frequency']:.4f}, "
                                f"原位置: {obj['original_position']}, "
                                f"新位置: {obj['new_position']}\n")
                    
                    if len(optimized_layout) > 20:
                        f.write("...\n")
                
                self.status_var.set(f"结果报告已保存至: {os.path.basename(file_path)}")
                messagebox.showinfo("成功", f"结果报告已成功导出至:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出结果报告失败: {str(e)}")
    
    def export_data(self):
        """导出优化数据"""
        if not self.optimization_result or not self.optimizer:
            messagebox.showerror("错误", "请先运行优化")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存优化数据",
            defaultextension=".out",
            filetypes=[("输出文件", "*.out"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 生成输出文件
                if self.optimizer.generate_output_file(file_path):
                    self.status_var.set(f"优化数据已保存至: {os.path.basename(file_path)}")
                    messagebox.showinfo("成功", f"优化数据已成功导出至:\n{file_path}")
                else:
                    messagebox.showerror("错误", "导出优化数据失败")
            except Exception as e:
                messagebox.showerror("错误", f"导出优化数据失败: {str(e)}")

def main():
    """主函数"""
    root = tk.Tk()
    app = StorageOptimizationSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
