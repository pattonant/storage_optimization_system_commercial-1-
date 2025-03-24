#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
华为云存储服务控制系统 - 命令行版本
主要功能：通过减少硬盘数据碎片化程度，提升系统整体效率
"""

import os
import sys
import json
import time
import argparse
from optimizer import StorageOptimizer

def print_header():
    """打印程序标题"""
    print("=" * 60)
    print("华为云存储服务控制系统 - 命令行版本")
    print("功能：通过减少硬盘数据碎片化程度，提升系统整体效率")
    print("=" * 60)
    print()

def print_progress(progress):
    """打印进度条"""
    bar_length = 40
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r进度: |{bar}| {progress:.1f}% ')
    sys.stdout.flush()
    if progress >= 100:
        print()

def load_data(file_path):
    """加载数据文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return None

def save_output(file_path, optimizer):
    """保存输出文件"""
    try:
        if optimizer.generate_output_file(file_path):
            print(f"成功保存输出文件: {file_path}")
            return True
        else:
            print("保存输出文件失败")
            return False
    except Exception as e:
        print(f"保存输出文件失败: {str(e)}")
        return False

def print_data_stats(optimizer):
    """打印数据统计信息"""
    if not optimizer or not optimizer.objects:
        print("没有可用的数据")
        return
    
    object_count = len(optimizer.objects)
    total_size = sum(obj['size'] for obj in optimizer.objects)
    avg_size = total_size / object_count if object_count > 0 else 0
    avg_freq = sum(obj['access_frequency'] for obj in optimizer.objects) / object_count if object_count > 0 else 0
    
    print("\n数据统计:")
    print(f"- 对象数量: {object_count}")
    print(f"- 总大小: {total_size:.2f} GB")
    print(f"- 平均大小: {avg_size:.2f} GB")
    print(f"- 平均访问频率: {avg_freq:.4f}")
    print(f"- 硬盘空间: {optimizer.disk_space} GB")
    print(f"- 令牌数: {optimizer.token_count}")

def print_optimization_result(result):
    """打印优化结果"""
    if not result:
        print("没有可用的优化结果")
        return
    
    print("\n优化结果:")
    print(f"- 算法: {result['algorithm']}")
    print(f"- 优化前碎片率: {result['before_fragmentation']:.2f}%")
    print(f"- 优化后碎片率: {result['after_fragmentation']:.2f}%")
    print(f"- 优化前性能得分: {result['before_score']:.2f}")
    print(f"- 优化后性能得分: {result['after_score']:.2f}")
    print(f"- 性能提升: {result['improvement']:.2f}%")
    print(f"- 优化耗时: {result['time_cost']:.2f} 秒")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='华为云存储服务控制系统 - 命令行版本')
    parser.add_argument('input_file', help='输入数据文件路径')
    parser.add_argument('output_file', help='输出结果文件路径')
    parser.add_argument('--algorithm', '-a', choices=['greedy', 'dp', 'heuristic'], 
                        default='greedy', help='优化算法: greedy(贪心算法), dp(动态规划), heuristic(启发式搜索)')
    parser.add_argument('--disk_space', '-d', type=float, default=1000.0, help='硬盘空间大小(GB)')
    parser.add_argument('--token_count', '-t', type=int, default=100, help='令牌数量')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    print_header()
    
    # 检查输入文件
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件不存在: {args.input_file}")
        return 1
    
    # 加载数据
    print(f"正在加载数据文件: {args.input_file}")
    content = load_data(args.input_file)
    if not content:
        return 1
    
    # 创建优化器
    optimizer = StorageOptimizer(args.disk_space, args.token_count)
    
    # 加载数据到优化器
    print("正在解析数据...")
    if not optimizer.load_data(content):
        print("数据解析失败")
        return 1
    
    # 打印数据统计信息
    print_data_stats(optimizer)
    
    # 算法映射
    algorithm_map = {
        'greedy': '贪心算法',
        'dp': '动态规划',
        'heuristic': '启发式搜索'
    }
    
    # 运行优化
    algorithm = algorithm_map[args.algorithm]
    print(f"\n开始使用{algorithm}进行优化...")
    
    result = optimizer.optimize(algorithm, print_progress)
    
    # 打印优化结果
    print_optimization_result(result)
    
    # 如果需要详细信息，打印优化后的对象布局
    if args.verbose:
        print("\n优化后的对象布局（前20个）:")
        optimized_layout = optimizer.get_optimized_layout()
        for i, obj in enumerate(optimized_layout[:20]):
            print(f"{i+1}. ID: {obj['id']}, 大小: {obj['size']:.2f} GB, "
                  f"访问频率: {obj['access_frequency']:.4f}, "
                  f"原位置: {obj['original_position']}, "
                  f"新位置: {obj['new_position']}")
        
        if len(optimized_layout) > 20:
            print("...")
    
    # 保存输出文件
    print(f"\n正在保存输出文件: {args.output_file}")
    if not save_output(args.output_file, optimizer):
        return 1
    
    print("\n优化完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
