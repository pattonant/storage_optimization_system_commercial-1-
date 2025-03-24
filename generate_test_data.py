#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据生成器
用于生成测试数据文件，以便测试存储优化系统
"""

import random
import os

def generate_test_data(file_path, object_count=100, disk_space=1000, token_count=100):
    """
    生成测试数据文件
    
    参数:
        file_path: 输出文件路径
        object_count: 对象数量
        disk_space: 硬盘空间大小（GB）
        token_count: 令牌数量
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # 写入第一行：硬盘空间和令牌数
            f.write(f"{disk_space} {token_count}\n")
            
            # 写入对象数据
            for i in range(1, object_count + 1):
                # 生成随机大小（0.1GB到10GB）
                size = random.uniform(0.1, 10.0)
                
                # 生成随机访问频率（0.1到1.0）
                access_freq = random.uniform(0.1, 1.0)
                
                # 写入对象数据行：ID 大小 访问频率
                f.write(f"{i} {size:.2f} {access_freq:.4f}\n")
        
        print(f"成功生成测试数据文件: {file_path}")
        print(f"- 对象数量: {object_count}")
        print(f"- 硬盘空间: {disk_space} GB")
        print(f"- 令牌数: {token_count}")
        
        return True
    except Exception as e:
        print(f"生成测试数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 生成测试数据文件
    output_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(output_dir, "sample_test.in")
    
    generate_test_data(test_file, object_count=100, disk_space=1000, token_count=100)
