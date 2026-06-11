#!/usr/bin/env python3
"""
半导体火灾股价走势图生成脚本
生成两张图表：
1. 归一化股价走势（2021-01-01=100）+ 火灾事件标记
2. 实际股价走势（当地货币）

保存到 blog/images/
"""

import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ====== 配置 ======
START_DATE = "2021-01-01"
END_DATE = "2026-06-01"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")

# 股票代码
TICKERS = {
    "2330.TW": "台积电 (TSMC)",
    "000660.KS": "SK海力士",
    "005930.KS": "三星电子",
    "MU": "美光 (Micron)"
}

# ====== 火灾/事故事件 ======
EVENTS = [
    # --- 台积电 ---
    ("2021-03-31", "台积电竹科12厂火警", "#E63946"),
    ("2021-04-14", "台积电晶圆14厂停电", "#E63946"),
    ("2021-10-21", "台积电南科再生水厂火灾", "#E63946"),
    ("2023-04-30", "台积电美国Fab21施工火灾", "#E63946"),
    ("2024-05-15", "台积电美国厂化学爆炸", "#E63946"),
    ("2025-01-21", "台积电嘉义外部火灾波及", "#E63946"),
    # --- SK海力士 ---
    ("2021-04-06", "SK海力士利川M16氢氟酸泄漏", "#2A9D8F"),
    ("2022-06-01", "SK海力士无锡新厂施工火灾(此前遗漏)", "#2A9D8F"),
    ("2026-06-01", "SK海力士清州厂火灾·氟化氢泄漏7伤⚠️", "#D62828"),
    # --- 三星 --- (无事件)
    # --- 美光 --- (无事件)
    # --- 其他 ---
    ("2021-03-19", "瑞萨电子那珂工厂火灾(参考)", "#7678ED"),
]

def download_data():
    """下载所有股票数据"""
    print("📥 下载数据中...")
    all_data = {}
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
            if df.empty:
                print(f"  ⚠️ {ticker}: 无数据")
                continue
            # Use 'Close' column
            close_col = 'Close'
            if close_col not in df.columns:
                print(f"  ⚠️ {ticker}: 无Close列, 列={list(df.columns)}")
                continue
            prices = df[close_col]
            if isinstance(prices, pd.DataFrame):
                prices = prices.iloc[:, 0]
            all_data[ticker] = prices
            print(f"  ✅ {ticker} ({TICKERS[ticker]}): {len(prices)} 天数据")
        except Exception as e:
            print(f"  ❌ {ticker}: {e}")
    return all_data


def normalize_series(series, base_date="2021-01-01"):
    """以指定日期为基准归一化 (base=100)"""
    base = series.loc[base_date:].iloc[0] if base_date in series.index else series.iloc[0]
    return series / base * 100


def plot_normalized(all_data, events):
    """绘制归一化股价走势图"""
    print("📈 绘制归一化图表...")
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    color_idx = 0
    
    for ticker, name in TICKERS.items():
        if ticker not in all_data:
            continue
        series = all_data[ticker]
        norm = normalize_series(series)
        ax.plot(norm.index, norm.values, label=name, linewidth=2, color=colors[color_idx % len(colors)])
        color_idx += 1
    
    # ——— 绘制事件标记 ———
    # 先收集每个公司的事件
    tsmc_events = [e for e in events if "台积电" in e[1]]
    skhynix_events = [e for e in events if "SK海力士" in e[1]]
    renesas_events = [e for e in events if "瑞萨" in e[1]]
    
    # 收集有可用数据的 ticker 的首日值
    def get_ticker_value(event_date_str, ticker_key):
        dt = pd.Timestamp(event_date_str)
        if ticker_key in all_data:
            series = all_data[ticker_key]
            # 找事件日或之后的第一个数据点
            mask = series.index >= dt
            if mask.any():
                idx = mask.argmax()
                val = normalize_series(series).iloc[idx]
                return float(val)
        return None
    
    # 台积电事件 → 用 2330.TW 基准值
    tsmc_norm = normalize_series(all_data["2330.TW"])
    def get_2330_val(dt_str):
        dt = pd.Timestamp(dt_str)
        mask = tsmc_norm.index >= dt
        if mask.any():
            return float(tsmc_norm[mask].iloc[0])
        return None
    
    sk_norm = normalize_series(all_data.get("000660.KS", all_data.get("005930.KS")))
    def get_sk_val(dt_str):
        if "000660.KS" not in all_data:
            return None
        dt = pd.Timestamp(dt_str)
        mask = sk_norm.index >= dt
        if mask.any():
            return float(sk_norm[mask].iloc[0])
        return None
    
    # 绘制事件标记
    event_handles = []
    event_labels = []
    
    for date_str, desc, color in events:
        dt = pd.Timestamp(date_str)
        
        # 确定标记在哪个系列上显示
        if "台积电" in desc:
            val = get_2330_val(date_str)
            series_label = "TSMC"
        elif "SK海力士" in desc:
            val = get_sk_val(date_str)
            series_label = "SK Hynix"
        elif "瑞萨" in desc:
            val = get_2330_val(date_str)  # 借用 TSMC
            series_label = "Ref"
        else:
            val = get_2330_val(date_str)
            series_label = "TSMC"
        
        if val is None:
            continue
        
        # 对 2026-06-01 事件使用特殊标记
        is_current_event = (date_str == "2026-06-01")
        
        if is_current_event:
            marker_size = 180
            marker_style = 'D'  # Diamond for special events
            edge_width = 3
        else:
            marker_size = 120
            marker_style = 'D'
            edge_width = 2
        
        scatter = ax.scatter(
            [dt], [val],
            marker=marker_style, s=marker_size,
            color=color, edgecolors='black',
            linewidth=edge_width, zorder=5,
            alpha=0.9
        )
        
        # 标注文字
        short_desc = desc.split('·')[0] if '·' in desc else desc
        if len(short_desc) > 12:
            short_desc = short_desc[:11] + '…'
        
        # 特殊处理 2026-06-01 事件的标注
        if is_current_event:
            offset_x = 3
            offset_y = val * 0.05 if val > 500 else 15
            bbox_props = dict(boxstyle="round,pad=0.4", facecolor=color, edgecolor='black',
                             linewidth=2, alpha=0.85)
            ax.annotate(
                f"⚠️ {date_str}\n{desc}",
                xy=(dt, val), xytext=(dt + timedelta(days=offset_x), val + offset_y),
                fontsize=9, fontweight='bold', color='white',
                bbox=bbox_props,
                arrowprops=dict(arrowstyle="->", color='black', lw=2),
                zorder=6
            )
        else:
            offset_y = val * 0.04 if val > 300 else 10
            ax.annotate(
                f"{date_str}\n{short_desc}",
                xy=(dt, val),
                xytext=(dt + timedelta(days=2), val + offset_y),
                fontsize=7, color=color, fontweight='bold',
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2, alpha=0.7),
                zorder=6
            )
    
    # 图表配置
    ax.set_title("全球主要半导体厂股价走势与火灾事故标记 (归一化, 2021-01-01=100)",
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel("归一化股价 (基准日=100)", fontsize=12)
    ax.set_xlabel("日期", fontsize=12)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45, ha='right')
    
    # 图注
    legend_text = (
        "◆ 火灾/事故事件标记\n"
        "◆ 特殊标记: 2026-06-01 SK海力士清州厂火灾(氟化氢泄漏,7人受伤)\n"
        "数据来源: Yahoo Finance | 基准日: 2021-01-01 = 100"
    )
    ax.text(0.02, 0.02, legend_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # 保存
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "semiconductor-fires-stock.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    print(f"  ✅ 保存: {path}")
    plt.close(fig)


def plot_actual(all_data, events):
    """绘制实际股价走势图"""
    print("📈 绘制实际股价图表...")
    fig, ax1 = plt.subplots(figsize=(20, 10))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    color_idx = 0
    
    # 主坐标轴：TSMC (TWD) 和 Micron (USD)
    ax1_tickers = ["2330.TW", "MU"]
    ax2_tickers = ["000660.KS", "005930.KS"]
    
    lines = []
    for ticker, name in TICKERS.items():
        if ticker not in all_data:
            continue
        series = all_data[ticker]
        if ticker in ax2_tickers:
            color = '#2ca02c' if 'SK' in name else '#d62728' if '三星' in name else colors[color_idx % len(colors)]
        else:
            color = colors[color_idx % len(colors)]
        
        if ticker in ax2_tickers:
            # 使用右侧 y 轴 (韩元)
            line = ax1.plot(series.index, series.values, label=name,
                           linewidth=2, color=color, alpha=0.85)
        else:
            line = ax1.plot(series.index, series.values, label=name,
                           linewidth=2, color=color)
        lines.extend(line)
        color_idx += 1
    
    # 左侧 y 轴 (TWD / USD)
    ax1.set_ylabel("股价 (TWD / USD)", fontsize=12, color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    
    # 右侧 y 轴 (韩元)
    ax2 = ax1.twinx()
    for ticker in ["000660.KS", "005930.KS"]:
        if ticker in all_data:
            series = all_data[ticker]
            name = TICKERS[ticker]
            color = '#2ca02c' if 'SK' in name else '#d62728' if '三星' in name else '#ff7f0e'
            line = ax2.plot(series.index, series.values, label=name,
                          linewidth=2, color=color, alpha=0.85)
            lines.extend(line)
    ax2.set_ylabel("股价 (韩元)", fontsize=12, color='#2ca02c')
    ax2.tick_params(axis='y', labelcolor='#2ca02c')
    
    # 事件标记（简化版）
    for date_str, desc, color in events:
        dt = pd.Timestamp(date_str)
        is_current = (date_str == "2026-06-01")
        
        # 找最近的 SK Hynix 数据点
        if "SK海力士" in desc and "000660.KS" in all_data:
            series = all_data["000660.KS"]
            mask = series.index >= dt
            if mask.any():
                val = float(series[mask].iloc[0])
                marker_size = 200 if is_current else 120
                marker_style = 'D' if is_current else 'D'
                edge_width = 3 if is_current else 2
                ax2.scatter([dt], [val], marker=marker_style, s=marker_size,
                          color=color, edgecolors='black', linewidth=edge_width, zorder=5, alpha=0.9)
                if is_current:
                    bbox_props = dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor='black', linewidth=2, alpha=0.85)
                    ax2.annotate(f"⚠️ {date_str}\n{desc}", xy=(dt, val),
                                xytext=(dt + timedelta(days=10), val * 1.1),
                                fontsize=8, fontweight='bold', color='white',
                                bbox=bbox_props,
                                arrowprops=dict(arrowstyle="->", color='black', lw=2))
        elif "台积电" in desc and "2330.TW" in all_data:
            series = all_data["2330.TW"]
            mask = series.index >= dt
            if mask.any():
                val = float(series[mask].iloc[0])
                ax1.scatter([dt], [val], marker='D', s=100,
                          color=color, edgecolors='black', linewidth=1.5, zorder=5, alpha=0.9)
                ax1.annotate(f"{date_str}", xy=(dt, val),
                           xytext=(dt + timedelta(days=5), val * 1.02),
                           fontsize=6, color=color, fontweight='bold',
                           arrowprops=dict(arrowstyle="->", color=color, lw=0.8, alpha=0.6))
    
    # 合并图例
    labels = [l.get_label() for l in lines]
    # 创建双轴图例
    ax1.legend(lines, labels, loc='upper left', fontsize=10, framealpha=0.9)
    
    ax1.set_title("全球主要半导体厂实际股价走势 (2021-2026)",
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel("日期", fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    path = os.path.join(OUTPUT_DIR, "semiconductor-fires-stock-actual.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    print(f"  ✅ 保存: {path}")
    plt.close(fig)


def main():
    print("=" * 60)
    print("  半导体火灾股价走势图生成")
    print("=" * 60)
    
    data = download_data()
    
    if not data:
        print("❌ 没有可用数据")
        return
    
    plot_normalized(data, EVENTS)
    plot_actual(data, EVENTS)
    
    print("\n✅ 所有图表已生成!")


if __name__ == "__main__":
    main()
