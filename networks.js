const result = require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');

if (result.error) {
  throw result.error;
}

const node_url =
    `${process.env.chainvoice_qnode_url}/${process.env.chainvoice_qnode_key}`;
const qadmin_key = process.env.chainvoice_qadmin_private_key;

module.exports = {
  networks: {
    development: {
      protocol: 'http',
      host: 'localhost',
      port: 8545,
      gas: 5000000,
      gasPrice: 5e9,
      networkId: '*',
    },
    chainvoice: {
      provider: () => new HDWalletProvider(
          qadmin_key, node_url
      ),
      networkId: '*',
      gasPrice: 0
    }
  },
};
