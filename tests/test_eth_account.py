import pytest
from lit_python_sdk import connect
import os
os.environ['ECC_BACKEND_CLASS'] = 'lit_python_sdk.lit_pkp_backend.LitPKPBackend'
from eth_account import Account

def test_sign():
    to_sign = "0xadb20420bde8cda6771249188817098fca8ccf8eef2120a31e3f64f5812026bf"
    account = Account.from_key("0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364")
    signature = account.unsafe_sign_hash(to_sign)
    print(signature)
