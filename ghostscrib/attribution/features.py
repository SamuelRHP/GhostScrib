"""TRACE-inspired token rank and transition feature extraction.

Reference:
    "Who Wrote the Book? Detecting and Attributing LLM Ghostwriters"
    (Shetty et al., EMNLP Main / arXiv 2603.28054).

Extracts token-level rank buckets, transition probability matrices, and predictive
entropy using a lightweight evaluator model (GPT-2 small on CPU by default).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple
import numpy as np

# 4 Canonical rank buckets: [0, 10), [10, 100), [100, 1000), [1000, inf)
RANK_BUCKETS = [(0, 10), (10, 100), (100, 1000), (1000, 1_000_000)]
N_BUCKETS = len(RANK_BUCKETS)


def get_rank_bucket(rank: int) -> int:
    """Map a 0-based token rank to its bucket index (0..3)."""
    for i, (low, high) in enumerate(RANK_BUCKETS):
        if low <= rank < high:
            return i
    return N_BUCKETS - 1


def compute_token_ranks_and_entropy(
    text: str,
    model_name: str = "gpt2",
    device: str = "cpu",
    max_length: int = 1024,
) -> Tuple[List[int], List[float], int]:
    """Tokenize and score text with the evaluator model.

    Returns:
        (bucket_sequence, entropy_sequence, total_token_count)
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        raise RuntimeError("torch and transformers are required for attribution scoring.")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    tokens = tokenizer.encode(text, return_tensors="pt")
    total_tokens = tokens.shape[1]

    bucket_sequence: List[int] = []
    entropy_sequence: List[float] = []

    # Process in non-overlapping or sliding 1024-token chunks
    with torch.no_grad():
        for start_idx in range(0, total_tokens - 1, max_length):
            chunk = tokens[:, start_idx : min(start_idx + max_length, total_tokens)].to(device)
            if chunk.shape[1] < 2:
                continue

            outputs = model(chunk)
            logits = outputs.logits[:, :-1, :]  # [1, seq_len-1, vocab_size]
            targets = chunk[:, 1:]              # [1, seq_len-1]

            # Softmax to probabilities
            probs = torch.softmax(logits, dim=-1)

            # Compute ranks
            # argsort descending gives rank of each vocabulary item
            sorted_indices = torch.argsort(probs, dim=-1, descending=True)
            for t in range(targets.shape[1]):
                target_token = targets[0, t].item()
                # Find rank of target token
                rank_tensor = (sorted_indices[0, t] == target_token).nonzero(as_tuple=True)[0]
                rank = rank_tensor.item() if len(rank_tensor) > 0 else 50000
                bucket_sequence.append(get_rank_bucket(rank))

                # Predictive entropy: -sum(p * log(p))
                p = probs[0, t]
                # Filter small probs to prevent log(0)
                mask = p > 1e-12
                p_masked = p[mask]
                entropy = -(p_masked * torch.log(p_masked)).sum().item()
                entropy_sequence.append(entropy)

    return bucket_sequence, entropy_sequence, total_tokens


def build_transition_feature_vector(
    bucket_seq: List[int],
    entropy_seq: List[float],
) -> np.ndarray:
    """Construct a normalized 22-dimensional feature vector.

    Components:
    - Rank bucket distribution (4 features)
    - Transition probability matrix between consecutive buckets (4x4 = 16 features)
    - Entropy mean and standard deviation (2 features)
    """
    if not bucket_seq:
        return np.zeros(22, dtype=np.float32)

    # 1. Bucket distribution (4-dim)
    bucket_counts = np.zeros(N_BUCKETS, dtype=np.float32)
    for b in bucket_seq:
        bucket_counts[b] += 1.0
    bucket_dist = bucket_counts / (len(bucket_seq) or 1.0)

    # 2. Transition matrix (16-dim)
    transition_counts = np.zeros((N_BUCKETS, N_BUCKETS), dtype=np.float32)
    for i in range(len(bucket_seq) - 1):
        src, dst = bucket_seq[i], bucket_seq[i + 1]
        transition_counts[src, dst] += 1.0

    # Row-normalize transitions (Laplace smoothed)
    transition_matrix = np.zeros((N_BUCKETS, N_BUCKETS), dtype=np.float32)
    for r in range(N_BUCKETS):
        row_sum = transition_counts[r].sum()
        if row_sum > 0:
            transition_matrix[r] = transition_counts[r] / row_sum
        else:
            transition_matrix[r] = 1.0 / N_BUCKETS

    transition_flat = transition_matrix.flatten()

    # 3. Entropy statistics (2-dim)
    if entropy_seq:
        mean_entropy = float(np.mean(entropy_seq))
        std_entropy = float(np.std(entropy_seq))
    else:
        mean_entropy = 0.0
        std_entropy = 0.0

    entropy_features = np.array([mean_entropy, std_entropy], dtype=np.float32)

    # Combine into 22-dimensional vector
    feature_vector = np.concatenate([bucket_dist, transition_flat, entropy_features])
    return feature_vector

