async function displayBlockchainData() {
    const blockchainData = await eel.get_blockchain_data()();

    const dataDiv = document.querySelector(".data");
    dataDiv.innerHTML = ""; // Clear the current content

    for (const blockData of blockchainData) {
        const blockDiv = document.createElement("div");
        console.log("data", blockData);

        // Create an HTML string for transactions
        const transactionsHtml = blockData.transactions.map((transaction) => {
            if (transaction && transaction.sender_public_key && transaction.receiver_public_key) {
                return `<li>Sender: ${transaction.sender_public_key}, Receiver: ${transaction.receiver_public_key}</li>`;
            } else {
                return '';
            }
        }).join('');

        blockDiv.innerHTML = `
            <h4>Block ${blockData.block_number}</h4>
            <p>Transactions:</p>
            <ul>${transactionsHtml}</ul>
            <p>Timestamp: ${blockData.timestamp}</p>
            <p>Previous hash: ${blockData.previous_hash}</p>
            <p>Hash: ${blockData.hash}</p>
        `;

        dataDiv.appendChild(blockDiv);
    }
}

// Call the function to display the blockchain data
displayBlockchainData();

// Set an interval to update the blockchain data every 5 seconds
setInterval(displayBlockchainData, 5000);
