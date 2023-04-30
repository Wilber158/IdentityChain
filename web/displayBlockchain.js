// Add this function to your JavaScript code
async function displayBlockchainData() {
    const blockchainData = await eel.get_blockchain_data()();

    const dataDiv = document.querySelector(".data");
    dataDiv.innerHTML = ""; // Clear the current content

    for (const blockData of blockchainData) {
        const blockDiv = document.createElement("div");

        blockDiv.innerHTML = `
            <h4>Block ${blockData.block_number}</h4>
            <p>Transactions: ${blockData.transactions}</p>
            <p>Timestamp: ${blockData.timestamp}</p>
            <p>Previous hash: ${blockData.previous_hash}</p>
            <p>Hash: ${blockData.hash}</p>
        `;

        dataDiv.appendChild(blockDiv);
    }
}

// Call the function to display the blockchain data
displayBlockchainData();
