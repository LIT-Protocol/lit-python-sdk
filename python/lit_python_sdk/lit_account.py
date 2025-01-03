from typing import (
    Any,
    Dict,
    Optional,
    cast,
)

from eth_keyfile.keyfile import (
    KDFType,
)
from eth_keys.datatypes import (
    PrivateKey,
)
from eth_typing import (
    ChecksumAddress,
    Hash32,
)

from eth_account.account_local_actions import (
    AccountLocalActions,
)
from eth_account.datastructures import (
    SignedMessage,
    SignedTransaction,
)
from eth_account.messages import (
    SignableMessage,
)
from eth_account.signers.base import (
    BaseAccount,
)
from eth_account.types import (
    Blobs,
    TransactionDictType,
)
from hexbytes import HexBytes

from lit_python_sdk.client import LitClient


class LitAccount(BaseAccount):
    r"""
    A an account controlled by a Lit Protocol PKP
    """

    def __init__(self, lit_client: LitClient | None = None):
        if lit_client is None:
            lit_client = LitClient()
            lit_client.create_wallet()
        self._lit_client = lit_client

        self._address: ChecksumAddress = lit_client.get_pkp()["ethAddress"]

    @property
    def address(self) -> ChecksumAddress:
        return self._address

    def unsafe_sign_hash(self, message_hash: Hash32) -> SignedMessage:
        return cast(
            SignedMessage,
            self._sign_hash(message_hash),
        )

    def sign_message(self, signable_message: SignableMessage) -> SignedMessage:
        """
        Generate a string with the encrypted key.

        This uses the same structure as in
        :meth:`~eth_account.account.Account.sign_message`, but without a
        private key argument.
        """
        return cast(
            SignedMessage,
            self._publicapi.sign_message(signable_message, private_key=self.key),
        )

    def sign_transaction(
        self, transaction_dict: TransactionDictType, blobs: Optional[Blobs] = None
    ) -> SignedTransaction:
         # allow from field, *only* if it matches the private key
        if "from" in transaction_dict:
            if transaction_dict["from"] == account.address:
                sanitized_transaction = dissoc(transaction_dict, "from")
            else:
                str_from = (
                    transaction_dict["from"].decode()
                    if isinstance(transaction_dict["from"], bytes)
                    else transaction_dict["from"]
                )
                raise TypeError(
                    f"from field must match key's {account.address}, but it was "
                    f"{str_from}"
                )
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            encoded_transaction,
        ) = sign_transaction_dict(account._key_obj, sanitized_transaction, blobs=blobs)
        transaction_hash = keccak(encoded_transaction)

        return SignedTransaction(
            raw_transaction=HexBytes(encoded_transaction),
            hash=HexBytes(transaction_hash),
            r=r,
            s=s,
            v=v,
        )
    
    def _sign_hash(
        self,
        message_hash: Hash32,
    ) -> SignedMessage:
        msg_hash_bytes = HexBytes(message_hash)
        if len(msg_hash_bytes) != 32:
            raise ValueError("The message hash must be exactly 32-bytes")

        response = self._lit_client.sign(msg_hash_bytes)
        v = response["v"]
        r = response["r"]
        s = response["s"]
        eth_signature_bytes = response["signature"]

        return SignedMessage(
            message_hash=msg_hash_bytes,
            r=r,
            s=s,
            v=v,
            signature=HexBytes(eth_signature_bytes),
        )

    def __bytes__(self) -> bytes:
        return self.key
