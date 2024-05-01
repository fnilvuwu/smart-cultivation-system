console.log("Hello");

const socket = io.connect();

socket.on("new_broadcast", (message) => {
  const broadcastMessage = document.getElementById("broadcastMessage");
  broadcastMessage.innerHTML = message;
});
