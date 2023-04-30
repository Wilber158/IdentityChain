document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("back-btn").addEventListener("click", function() {
        // Add your register button functionality here
        window.location.href = "main.html";
    });

    const submitButton = document.querySelector('button[type="submit"]');

    submitButton.addEventListener('click', async (event) => {
        const pbDir = document.getElementById("pb-dir").innerHTML;
        const pvDir = document.getElementById("pv-dir").innerHTML;
        const name = document.getElementById("Name").value;
        const dob = document.getElementById("DOB").value;
        const address = document.getElementById("Address").value;
        const signature = document.getElementById("Signature").value;
        const shareWithSelf = (pbDir === pvDir);

        if (pbDir !== "" && pvDir !== "" && name !== "" && dob !== "" && address !== "" && signature !== "") {
            const personData = { "name": name, "dob": dob, "address": address, "signature": signature };
            const result = await eel.user_transaction(pvDir, pbDir, pbDir, JSON.stringify(personData), shareWithSelf)();
            if (result === "Transaction sent successfully.") {
                alert(result);
            } else {
                alert("Error: " + result);
            }
        } else {
            alert("Please fill in all the fields and select the directories");
        }
    });

    document.getElementById("pb-button").addEventListener("click", async function(){
        event.preventDefault();
        const directory = await eel.select_file_directory()();
        document.getElementById("pb-dir").innerHTML = directory;
    });

    document.getElementById("pvt-button").addEventListener("click", async function(){
        event.preventDefault();
        const directory = await eel.select_file_directory()();
        document.getElementById("pv-dir").innerHTML = directory;
    });
});
