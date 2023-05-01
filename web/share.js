document.addEventListener("DOMContentLoaded", function() {

    // Back button functionality
    document.getElementById("back-btn").addEventListener("click", function() {
      window.location.href = "main.html";
    });
  
 
  
    // Function to get user input values
    function getUserInput() {
      // Get user input values
      const name = document.getElementById("Name").value;
      const dob = document.getElementById("DOB").value;
      const address = document.getElementById("Address").value;
    
      // Check if at least one field is filled
      if (!name && !dob && !address) {
        alert("Please fill in at least one field");
        return null;
      }
    
      // Create user object with input values
      const user = {
        name: name,
        dob: dob,
        address: address
      };
    
      return user;
    }
  
    // Share data button functionality
    document.getElementById("submit").addEventListener("click", async function(){
      event.preventDefault();
      const user = getUserInput();
      if (user) {
        const public_dir = document.getElementById("pb-dir").innerHTML;
        const private_dir = document.getElementById("pv-dir").innerHTML;
        const receiver_public_key = document.getElementById("rc-dir").innerHTML;
        const result = await eel.user_share_transaction(private_dir, public_dir, receiver_public_key, JSON.stringify(user))();
        if (result === "Transaction sent successfully.") {
          alert(result);
        } else {
            alert("Error: " + result);
        }
        } else {
        alert("Please fill in all the fields and select the directories");
        }
      });
  
    // Directory buttons functionality
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

    document.getElementById("rc-button").addEventListener("click", async function(){
        event.preventDefault();
        const directory = await eel.select_file_directory()();
        document.getElementById("rc-dir").innerHTML = directory;
    });

  
  });
  
  
  


  