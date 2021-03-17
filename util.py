import hashlib
import base64
from algosdk import account, mnemonic

def generate_new_account():
	"""
	Generate a new Algorand account and print the public address
	and private key mnemonic.
	"""
	private_key, public_address = account.generate_account()
	passphrase = mnemonic.from_private_key(private_key)
	print("Address: {}\nPassphrase: \"{}\"".format(public_address, passphrase))
	return private_key, passphrase

def wait_for_confirmation(client, txid):
	"""
	Utility to function to wait until the transaction is
	confirmed before proceeding.

	@txid: C{string} - The transaction id of the asset
	"""
	last_round = client.status().get('last-round')
	while True:
		txinfo = client.pending_transaction_info(txid)
		print(txinfo)
		if txinfo.get('round') and txinfo.get('round') > 0:
			print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('round')))
			return txinfo
		else:
			print("Waiting for confirmation...")
			print('txinfo round', txinfo.get('round'))
			last_round = last_round + 1
			client.status_after_block(last_round)

def hash_file_data(filename, return_type="bytes"):
	"""
	Takes any byte data and returns the SHA512/256 hash in base64.
	"""
	filebytes = open(filename, 'rb').read()
	h = hashlib.sha256()
	h.update(filebytes)
	if return_type == "bytes":
		return h.digest()
	elif return_type == "base64":
		return base64.b64encode(h.digest())

def add_network_params(tx_data, client):
	"""
	Adds network-related parameters to transaction data.
	"""
	print(client)
	params = client.suggested_params()
	gen = params.gen
	gh = params.gh
	first_valid_round = params.first
	last_valid_round = params.last
	fee = params.min_fee
	tx_data["fee"] = fee
	tx_data["first"] = first_valid_round
	tx_data["last"] = last_valid_round
	tx_data["gh"] = gh
	tx_data["gen"] = gen
	return tx_data

def sign_and_send(txn, passphrase, client):
	"""
	Signs and sends the transaction to the network.
	Returns transaction info.
	"""
	private_key = mnemonic.to_private_key(passphrase)
	stxn = txn.sign(private_key)
	txid = stxn.transaction.get_txid()
	client.send_transaction(stxn)
	txinfo = wait_for_confirmation(client, txid)
	return txinfo

def balance_formatter(amount, asset_id, client):
	"""
	Returns the formatted units for a given asset and amount. 
	"""
	asset_info = client.asset_info(asset_id)
	decimals = asset_info.get("decimals")
	unit = asset_info.get("unitname")
	formatted_amount = amount/10**decimals
	return "{} {}".format(formatted_amount, unit)
	