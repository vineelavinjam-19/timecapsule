function sendMessage() {
    const email = document.getElementById("email").value;
    const message = document.getElementById("message").value;
    const sendAt = document.getElementById("send_at").value;
    const status = document.getElementById("status");

    if (!email || !message || !sendAt) {
        status.innerText = "❌ Please fill all required fields";
        return;
    }

    const data = {
        email: email,
        message: message,
        send_at: sendAt
    };

    fetch("http://127.0.0.1:5000/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        if(result.status === "saved") {
            status.innerText = "✅ Message Scheduled Successfully!";
        } else {
            status.innerText = "❌ Error: " + result.message;
        }
    })
    .catch(err => {
        console.error(err);
        status.innerText = "❌ Failed to schedule message";
    });
}
fetch("https://timecapsule-7qv4.onrender.com/save", {
    method: "POST",
    body: formData
})
