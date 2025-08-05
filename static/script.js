let digits = [];
let autoMode = false;

function setToken() {
  const token = document.getElementById("token").value;
  fetch("/set-token", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  }).then(() => {
    alert("Connected to Deriv. Starting stream...");
    startPolling();
  });
}

function tradeManual() {
  const direction = document.getElementById("strategy").value;
  const amount = document.getElementById("stake").value;

  fetch("/trade", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction, amount })
  }).then(res => res.json()).then(data => {
    document.getElementById("trade-result").innerText = data.status || data.error;
  });
}

function toggleAuto() {
  autoMode = document.getElementById("auto-mode").checked;
  fetch("/auto-toggle", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state: autoMode })
  }).then(res => res.json()).then(data => {
    console.log(data.status);
  });
}

function startPolling() {
  setInterval(() => {
    fetch("/latest")
      .then(res => res.json())
      .then(data => {
        const digit = data.digit;
        const digitsArray = data.digits || [];
        digits = digitsArray;
        const balance = data.account?.balance || 0;
        const currency = data.account?.currency || "";
        const loginid = data.account?.account_type || "-";
        const win = data.win || 0;
        const loss = data.loss || 0;

        // Update UI
        document.getElementById("latest-digit").innerText = digit ?? "-";
        document.getElementById("digit-history").innerText = digitsArray.join(" ");
        document.getElementById("account-balance").innerText = `${balance} ${currency}`;
        document.getElementById("account-type").innerText = loginid;
        document.getElementById("win-loss").innerText = `Wins: ${win} | Losses: ${loss}`;

        // AI Prediction logic
        let evenCount = digitsArray.filter(d => d % 2 === 0).length;
        let oddCount = digitsArray.length - evenCount;

        let prediction = "-";
        let confidence = "-";
        let safety = "WAIT";

        if (digitsArray.length >= 10) {
          if (oddCount >= 7) {
            prediction = "EVEN";
            confidence = Math.round((oddCount / digitsArray.length) * 100) + "%";
            safety = "EXCELLENT";
          } else if (evenCount >= 7) {
            prediction = "ODD";
            confidence = Math.round((evenCount / digitsArray.length) * 100) + "%";
            safety = "EXCELLENT";
          } else {
            prediction = (digit % 2 === 0) ? "ODD" : "EVEN";
            confidence = "50%";
            safety = "LOW";
          }

          document.getElementById("prediction").innerText = prediction;
          document.getElementById("confidence").innerText = confidence;
          document.getElementById("safety").innerText = safety;

          if (autoMode && safety === "EXCELLENT") {
            const strategy = prediction.toLowerCase(); // 'even' or 'odd'
            const amount = document.getElementById("stake").value;
            fetch("/trade", {
              method: "POST",
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ direction: strategy, amount })
            });
          }
        }

        if (data.result) {
          document.getElementById("trade-result").innerText = data.result;
        }
      });
  }, 1000);
}