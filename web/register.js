let mnemonic_seed = null;

async function init() {
    await display_mnemonic();
}

async function display_mnemonic() {
    const jsonString = await eel.generateMnemonicPhrase()();
    const result = JSON.parse(jsonString);
    const phrase = result.words;
    const seed = result.seed;
    const mnemonicWords = phrase.split(" ");
    const mnemonicContainer = document.getElementById("mnemonic-phrase");
    mnemonicWords.forEach(word => {
        const wordElement = document.createElement("span");
        wordElement.innerText = word;
        wordElement.className = "mnemonic-word";
        mnemonicContainer.appendChild(wordElement)
    });
    mnemonic_seed = seed; // Update the global variable with the seed value
}


async function selectDirectory() {
    let dir = await eel.select_directory()();
    document.getElementById("directory").innerHTML = dir;
}

document.getElementById("confirm-btn").addEventListener("click", async () => {
    const directory = document.getElementById("directory").innerHTML;
    const file_name = document.getElementById("file_name").value;
    if (directory !== "Directory" && file_name !== "") {
        console.log(mnemonic_seed); // Access the seed value here
        console.log(directory);
        await eel.create_user_node(mnemonic_seed, file_name, directory)();
        show_alert("File saved successfully");
        
    } else {
        show_alert("Please select a directory and enter a file name");
    }

    window.location.href = "main.html"
});

init();

document.getElementById("back-btn").addEventListener("click", function () {
    // Add your register button functionality here
    window.location.href = "main.html";
});

document.getElementById("share-btn").addEventListener("click", function () {
    // Add your register button functionality here
    window.location.href = "share.html";
});
document.getElementById("select-dir-btn").addEventListener("click", selectDirectory);
