// const chatBox = document.getElementById("chat-box");
// const input = document.getElementById("user-input");

// function appendMessage(text, sender) {
//   const msg = document.createElement("div");
//   msg.classList.add("message", sender);
//   msg.innerText = text;
//   chatBox.appendChild(msg);

//   chatBox.scrollTop = chatBox.scrollHeight;
// }

// async function sendMessage() {
//   const userText = input.value.trim();
//   if (!userText) return;

//   appendMessage(userText, "user");
//   input.value = "";

//   try {
//     const response = await fetch("http://localhost:8000/query", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({ query: userText }),
//     });

//     const data = await response.json();
//     appendMessage(data.response, "bot");

//   } catch (err) {
//     appendMessage("Error: " + err.message, "bot");
//   }
// }

// // Enter key support
// input.addEventListener("keypress", function (e) {
//   if (e.key === "Enter") {
//     sendMessage();
//   }
// });