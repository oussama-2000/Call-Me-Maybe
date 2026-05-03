"""
    tensor is a mathematical object that generate scalars, vecores and matrices
    tensor is any object build into torch
"""

import torch

#  creation:

data = [1, 2, 3]
my_tensor = torch.tensor(data=data)

# tensor attributes

tensor = torch.rand(2, 2)
print(f"data: {tensor}")
print(f"shape: {tensor.shape}")
print(f"device: {tensor.device}")
print(f"data type: {tensor.dtype}")
