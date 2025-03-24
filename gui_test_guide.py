#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - GUI测试指南
"""

import os
import sys

def print_test_guide():
    """打印GUI测试指南"""
    print("=" * 80)
    print("华为云存储服务控制系统 - GUI测试指南")
    print("=" * 80)
    print("\n本文档提供了如何在本地环境中测试GUI界面的详细说明。\n")
    
    print("1. 环境准备")
    print("-" * 40)
    print("在运行GUI版本之前，请确保您的环境中已安装以下依赖：")
    print("- Python 3.7或更高版本")
    print("- tkinter库（Python的标准GUI库）")
    print("- matplotlib库（用于数据可视化）")
    print("- numpy库（用于数据处理）")
    print("\n安装依赖的命令：")
    print("pip install matplotlib numpy")
    print("注意：tkinter通常随Python一起安装，如果缺少，请参考操作系统相关说明安装。")
    
    print("\n2. 运行GUI程序")
    print("-" * 40)
    print("在命令行中执行以下命令运行GUI程序：")
    print("python main_gui.py")
    print("\n程序启动后，您将看到一个现代化的界面，包含三个主要选项卡：")
    print("- 数据导入：用于导入数据文件")
    print("- 系统优化：用于设置优化参数并运行优化算法")
    print("- 结果分析：用于查看优化结果和可视化图表")
    
    print("\n3. 功能测试步骤")
    print("-" * 40)
    print("请按照以下步骤测试GUI功能：")
    
    print("\n3.1 数据导入测试")
    print("a) 点击"浏览..."按钮，选择sample_test.in测试数据文件")
    print("b) 点击"导入数据"按钮，系统将解析数据并显示数据预览")
    print("c) 检查数据统计信息是否正确显示（对象数量、总大小等）")
    
    print("\n3.2 系统优化测试")
    print("a) 在"优化参数"区域，设置硬盘空间和令牌数")
    print("b) 从下拉菜单中选择优化算法（贪心算法、动态规划或启发式搜索）")
    print("c) 点击"开始优化"按钮，观察进度条和日志更新")
    print("d) 等待优化完成，系统将自动切换到结果分析选项卡")
    
    print("\n3.3 结果分析测试")
    print("a) 检查优化统计信息是否正确显示（碎片率、性能得分等）")
    print("b) 从下拉菜单中选择可视化类型（碎片分布图、性能对比图或对象布局图）")
    print("c) 点击"生成图表"按钮，查看生成的图表")
    print("d) 点击"导出结果报告"按钮，选择保存位置，检查导出的报告内容")
    print("e) 点击"导出优化数据"按钮，选择保存位置，检查导出的数据文件")
    
    print("\n4. 界面特性")
    print("-" * 40)
    print("在测试过程中，请注意以下界面特性：")
    print("- 现代化设计：扁平化设计风格，清晰的色彩方案")
    print("- 响应式布局：调整窗口大小，观察界面是否自适应调整")
    print("- 用户友好性：操作流程是否直观，提示信息是否清晰")
    print("- 可视化效果：图表是否美观，数据展示是否清晰")
    
    print("\n5. 常见问题")
    print("-" * 40)
    print("Q: 运行程序时提示"No module named 'tkinter'"")
    print("A: 这表示您的Python环境中缺少tkinter库。在Linux上，可以使用包管理器安装：")
    print("   sudo apt-get install python3-tk（Ubuntu/Debian）")
    print("   sudo yum install python3-tkinter（CentOS/RHEL）")
    
    print("\nQ: 运行程序时提示"No module named 'matplotlib'"或"No module named 'numpy'"")
    print("A: 使用pip安装缺少的库：")
    print("   pip install matplotlib numpy")
    
    print("\nQ: 图表显示不正常或界面样式异常")
    print("A: 这可能是由于不同操作系统的主题差异导致的。程序会尝试使用'clam'主题，")
    print("   如果不可用，将回退到默认主题。这不会影响功能，只会略微改变外观。")
    
    print("\n6. 比赛提交说明")
    print("-" * 40)
    print("对于比赛评测环境，请使用命令行版本（main.py），而不是GUI版本：")
    print("python main.py <input_file> <output_file> [options]")
    print("\n命令行版本不依赖tkinter和matplotlib，可以在任何Python环境中运行。")
    
    print("\n" + "=" * 80)
    print("测试指南结束。如有任何问题，请参考README.md文档或联系开发者。")
    print("=" * 80)

if __name__ == "__main__":
    print_test_guide()
