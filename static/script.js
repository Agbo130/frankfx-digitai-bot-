let digits = [];

function setToken() {
  const token = document.getElementById("token").value;
  fetch("/set-token", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  }).then(() => {
    alert("Connected to Deriv!");
    startPolling();
  });
}

function trade(direction) {
  const amount = document.getElementById("stake").value;
  fetch("/trade", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction, amount })
  }).then(res => res.json()).then(data => {
    document.getElementById("trade-result").innerText = data.status || data.error;
  });
}

function startPolling() {
  setInterval(() => {
    fetch("/latest")
      .then(res => res.json())
      .then(data => {
        const digit = data.digit;
        const historyDiv = document.getElementById("digit-history");

        if (digit !== null) {
          digits.push(digit);
          if (digits.length > 20) digits.shift();

          document.getElementById("latest-digit").innerText = digit;
          historyDiv.innerText = digits.join(" ");

          const evenCount = digits.filter(d => d % 2 === 0).length;
          const oddCount = digits.length - evenCount;

          let prediction = "-";
          let confidence = "-";
          let safety = "WAIT";

          if (digits.length >= 10) {
            if (oddCount >= 7) {
              prediction = "EVEN";
              confidence = Math.round((oddCount / digits.length) * 100) + "%";
              safety = "EXCELLENT";
            } else if (evenCount >= 7) {
              prediction = "ODD";
              confidence = Math.round((evenCount / digits.length) * 100) + "%";
              safety = "EXCELLENT";
            } else {
              prediction = (digit % 2 === 0) ? "ODD" : "EVEN";
              confidence = "50%";
              safety = "MEDIUM";
            }
          }

          document.getElementById("prediction").innerText = prediction;
          document.getElementById("confidence").innerText = confidence;
          document.getElementById("safety").innerText = safety;
        }

        if (data.result) {
          document.getElementById("trade-result").innerText = data.result;
        }
      });
  }, 1000);
}