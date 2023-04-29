// This is just a dummy mnemonic phrase for demonstration purposes
const dummyMnemonicPhrase = "pistol maple duty lunch canyon critic critic lava mom canyon critic critic";

const mnemonicWords = dummyMnemonicPhrase.split(" ");
const mnemonicContainer = document.getElementById("mnemonic-phrase");

mnemonicWords.forEach(word => {
    const wordElement = document.createElement("span");
    wordElement.innerText = word;
    wordElement.className = "mnemonic-word";
    mnemonicContainer.appendChild(wordElement);
});


document.getElementById("confirm-btn").addEventListener("click", function() {
    // Add your confirm button functionality here
});

async function selectDirectory(){
    await eel.select_directory()();
}

document.getElementById("back-btn").addEventListener("click", function() {
    // Add your register button functionality here
    window.location.href = "main.html";
});
document.getElementById("select-dir-btn").addEventListener("click", selectDirectory);
