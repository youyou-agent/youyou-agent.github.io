#!/usr/bin/env python3
"""
SSD 写入放大（Write Amplification, WA）最小模拟器
--------------------------------------------------
用一个 log-structured FTL 模型说明：为什么 SSD 越满越慢。

规则：
  * NAND 只能按「块」擦除（erase），按「页」写入（program）。
  * 主机改写一个逻辑页 = 新写一页，旧页变成垃圾（invalid）。
  * 空闲块不足时触发垃圾回收（GC）：挑一个有效页最少的块，
    把里面还活着的页搬走，再整块擦除回收。
  * 写入放大 WA = NAND 实际写入页数 / 主机请求写入页数。

只需标准库，直接 `python3 write-amplification-demo.py` 即可跑。
"""

import random

BLOCK_PAGES = 128      # 每个 NAND 块的页数（擦除单位）
TOTAL_BLOCKS = 200     # 总块数
HOST_WRITES = 200000   # 主机改写次数
RESERVE = 2            # 保留几个空闲块做 GC 周转


class Ssd:
    def __init__(self, fill: float, seed: int = 7, strategy: str = "greedy"):
        self.rnd = random.Random(seed)
        self.strategy = strategy
        self.total_pages = BLOCK_PAGES * TOTAL_BLOCKS
        self.lba_count = int(fill * self.total_pages)   # 主机可见逻辑页数

        self.pages = [[] for _ in range(TOTAL_BLOCKS)]  # 每块放了哪些逻辑页
        self.valid = [0] * TOTAL_BLOCKS                 # 每块的有效页数
        self.map = {}                                   # lba -> 当前所在块
        self.free = list(range(TOTAL_BLOCKS))
        self.open_blk = None
        self.in_gc = 0

        self.nand = 0      # NAND 写入页数
        self.erases = 0    # 擦除次数
        self.host = 0      # 主机写入页数

    # ---------- 底层：写一个物理页 ----------
    def _open_new(self):
        # 正常路径：留足周转块；GC 内部：只要有块可拿就行，避免互相递归
        if self.in_gc:
            while not self.free:
                self._gc_once()
        else:
            while len(self.free) <= RESERVE:
                self._gc_once()
        self.open_blk = self.free.pop()

    def _append(self, lba: int):
        if self.open_blk is None or len(self.pages[self.open_blk]) >= BLOCK_PAGES:
            self._open_new()
        b = self.open_blk
        old = self.map.get(lba)
        if old is not None and old != b:
            self.valid[old] -= 1
        self.pages[b].append(lba)
        self.valid[b] += 1
        self.map[lba] = b
        self.nand += 1

    # ---------- 垃圾回收 ----------
    def _pick_victim(self):
        cands = [b for b in range(TOTAL_BLOCKS)
                 if b != self.open_blk and self.pages[b]]
        if not cands:
            return None
        if self.strategy == "greedy":       # 真·SSD 主控：挑最脏的块
            return min(cands, key=lambda b: self.valid[b])
        return self.rnd.choice(cands)       # 对照组：随机挑块

    def _gc_once(self):
        victim = self._pick_victim()
        if victim is None:
            raise RuntimeError("no reclaimable block")

        self.in_gc += 1
        try:
            alive = [lba for lba in self.pages[victim] if self.map.get(lba) == victim]
            for lba in alive:              # 搬运活页 = 额外 NAND 写入
                if self.map.get(lba) == victim:
                    self._append(lba)
            self.pages[victim] = []        # erase
            self.valid[victim] = 0
            self.free.append(victim)
            self.erases += 1
        finally:
            self.in_gc -= 1

    # ---------- 主机侧 ----------
    def write(self, lba: int):
        self.host += 1
        self._append(lba)

    def run(self, n: int) -> dict:
        for _ in range(n):
            self.write(self.rnd.randrange(self.lba_count))
        return {
            "fill": self.lba_count / self.total_pages,
            "host": self.host,
            "nand": self.nand,
            "wa": self.nand / self.host,
            "erases": self.erases,
        }


def main():
    print(f"{'占用率':>7} {'策略':>8} {'主机写(页)':>12} {'NAND写(页)':>12} "
          f"{'写入放大':>9} {'擦除次数':>9}")
    print("-" * 66)
    for fill in (0.50, 0.70, 0.80, 0.90):
        for strat in ("greedy", "random"):
            r = Ssd(fill, strategy=strat).run(HOST_WRITES)
            print(f"{r['fill']:>6.0%} {strat:>8} {r['host']:>12,} {r['nand']:>12,} "
                  f"{r['wa']:>9.2f} {r['erases']:>9,}")

    print("\n对照组说明：greedy = 每次回收最脏的块（真 SSD 的做法）；")
    print("            random = 随机挑块（教科书里 1/(1−u) 公式的假设）")
    print("\n理论稳态近似（随机挑块）：WA ≈ 1 / (1 − 占用率)")
    for fill in (0.50, 0.70, 0.80, 0.90, 0.95):
        print(f"  占用率 {fill:>4.0%} → 理论 WA ≈ {1 / (1 - fill):.2f}")


if __name__ == "__main__":
    main()
