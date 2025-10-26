# ============================================================
# transactional_database_support.py
# For DM2025-Lab1 Phase 2: Frequent Pattern Mining (FP-Growth)
# ============================================================

import pandas as pd
from collections import defaultdict, Counter


class TransactionalDatabase:
    def __init__(self, filename):
        """Initialize with CSV file path."""
        self.filename = filename
        self.transactions = []
        self.item_freq = Counter()
        self.num_transactions = 0

    # ------------------------------------------------------------
    # 讀取交易資料
    # ------------------------------------------------------------
    def run(self):
        """讀取交易資料 (自動支援空白/tab 分隔)"""
        with open(self.filename, 'r', encoding='utf-8') as f:
            for line in f:
                tokens = [tok.strip() for tok in line.strip().split() if tok.strip()]
                if tokens:
                    self.transactions.append(tokens)
                    self.item_freq.update(tokens)
        self.num_transactions = len(self.transactions)

    # ------------------------------------------------------------
    def printStats(self):
        """輸出交易資料統計資訊"""
        print("=======================================")
        print(f"Total transactions: {self.num_transactions}")
        print(f"Unique items: {len(self.item_freq)}")
        print("Top 10 frequent items:")
        for item, freq in self.item_freq.most_common(10):
            print(f"  {item}: {freq}")
        print("=======================================")

    def getTransactions(self):
        return self.transactions

    def getItemFrequency(self):
        return dict(self.item_freq)

    # ------------------------------------------------------------
    # Frequent pattern mining
    # ------------------------------------------------------------
    def find_frequent_patterns(self, min_support):
        """
        FP-Growth-like pattern mining (simplified)
        Args:
            min_support (int): 最小支持度閾值
        Returns:
            dict: {pattern(tuple): support_count}
        """
        freq_items = {i for i, c in self.item_freq.items() if c >= min_support}
        if not freq_items:
            return {}

        filtered_trans = []
        for trans in self.transactions:
            filtered = [i for i in trans if i in freq_items]
            if filtered:
                filtered_trans.append(sorted(filtered))
        return self._fpgrowth_recursive(filtered_trans, min_support)

    def _fpgrowth_recursive(self, transactions, min_support, prefix=None):
        """簡化版 FP-growth 遞迴"""
        if prefix is None:
            prefix = []

        # 計算每個 item 出現次數
        item_counter = Counter()
        for trans in transactions:
            for item in trans:
                item_counter[item] += 1

        # 篩出符合 min_support 的 items
        freq_items = {i: c for i, c in item_counter.items() if c >= min_support}
        patterns = {}

        for item, support in freq_items.items():
            new_pattern = prefix + [item]
            patterns[tuple(new_pattern)] = support

            # 建立 conditional pattern base
            conditional_trans = []
            for trans in transactions:
                if item in trans:
                    index = trans.index(item)
                    conditional_trans.append(trans[:index])
            # 遞迴尋找更長的 frequent pattern
            sub_patterns = self._fpgrowth_recursive(conditional_trans, min_support, prefix + [item])
            patterns.update(sub_patterns)
        return patterns

    # ------------------------------------------------------------
    def get_support(self, pattern):
        """計算指定 pattern 的支持度"""
        count = 0
        for trans in self.transactions:
            if all(item in trans for item in pattern):
                count += 1
        return count

    # ------------------------------------------------------------
    def filter_transactions(self, min_length=1, max_length=None):
        """過濾交易筆數（可用於資料清理）"""
        filtered = []
        for trans in self.transactions:
            if len(trans) >= min_length and (max_length is None or len(trans) <= max_length):
                filtered.append(trans)
        self.transactions = filtered
        self.num_transactions = len(filtered)
