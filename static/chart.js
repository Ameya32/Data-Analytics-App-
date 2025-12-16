const sym1Select = document.getElementById("sym1");
const sym2Select = document.getElementById("sym2");

// PRICE CHART
const priceCtx = document.getElementById("priceChart").getContext("2d");
const priceChart = new Chart(priceCtx, {
  type: "line",
  data: { labels: [], datasets: [{ label: "Price", data: [] }] }
});

// SPREAD CHART
const spreadCtx = document.getElementById("spreadChart").getContext("2d");
const tfSelect = document.getElementById("timeframe");
const zInput = document.getElementById("zThreshold");

const spreadChart = new Chart(spreadCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      { label: "Spread", data: [], borderColor: "blue", yAxisID: "y" },
      { label: "Z-Score", data: [], borderColor: "red", yAxisID: "y1" }
    ]
  },
  options: {
    scales: {
      y1: { position: "right", grid: { drawOnChartArea: false } }
    }
  }
});

// CORRELATION CHART
const corrCtx = document.getElementById("corrChart").getContext("2d");
const corrChart = new Chart(corrCtx, {
  type: "line",
  data: { labels: [], datasets: [{ label: "Correlation", data: [] }] }
});


// async function loadPrice() {
//   const sym = sym1Select.value;
//   const res = await fetch(`/api/prices?symbol=${sym}`);
//   const data = await res.json();
//   console.log("DEBUG Price Data:", data.slice(-5)); // debug last 5 points

//   priceChart.data.labels = data.map(d => d.ts);
//   priceChart.data.datasets[0].data = data.map(d => d.price);
//   priceChart.data.datasets[0].label = sym;
//   priceChart.update();
// }

async function loadPrice() {
  const sym = sym1Select.value;
  const tf = tfSelect.value;

  const res = await fetch(`/api/prices_v2?symbol=${sym}&tf=${tf}`);
  const data = await res.json();

  console.log("DEBUG Price V2:", data.slice(-5));

  priceChart.data.labels = data.map(d => d.ts);
  priceChart.data.datasets[0].data = data.map(d => d.price);
  priceChart.data.datasets[0].label = `${sym} (${tf})`;
  priceChart.update();
}


async function loadSpread() {
  const s1 = sym1Select.value;
  const s2 = sym2Select.value;

  const res = await fetch(`/api/spread?s1=${s1}&s2=${s2}`);
  const data = await res.json();
  console.log("DEBUG Spread Data:", data.slice(-5)); 

  spreadChart.data.labels = data.map(d => d.ts);
  spreadChart.data.datasets[0].data = data.map(d => d.spread);
  spreadChart.data.datasets[1].data = data.map(d => d.zscore);
  spreadChart.update();
}

async function loadCorrelation() {
  const s1 = sym1Select.value;
  const s2 = sym2Select.value;

  const res = await fetch(`/api/correlation?s1=${s1}&s2=${s2}`);
  const data = await res.json();
  console.log("DEBUG Correlation Data:", data.slice(-5)); 

  corrChart.data.labels = data.map(d => d.ts);
  corrChart.data.datasets[0].data = data.map(d => d.corr);
  corrChart.update();
}

async function loadStats() {
  const sym = sym1Select.value;
  const res = await fetch(`/api/stats?symbol=${sym}`);
  const stats = await res.json();

  const table = document.getElementById("statsTable");
  table.innerHTML = "";

  for (const [k, v] of Object.entries(stats)) {
    table.innerHTML += `<tr><td>${k}</td><td>${v.toFixed(5)}</td></tr>`;
  }
}

async function loadAlerts() {
  const s1 = sym1Select.value;
  const s2 = sym2Select.value;
  const tf = tfSelect.value;
  const z = zInput.value;

  const res = await fetch(
    `/api/alerts_v2?s1=${s1}&s2=${s2}&tf=${tf}&z=${z}`
  );
  const alerts = await res.json();

  const alertBox = document.getElementById("alertBox");
  // alert(zscore.toFixed(2))
  if (alerts.length > 0) {
    const last = alerts[alerts.length - 1];

    alertBox.innerHTML = `
      🚨 ALERT<br>
      Pair: ${s1.toUpperCase()} / ${s2.toUpperCase()}<br>
      Z-Score: ${last.zscore.toFixed(2)}<br>
      Time: ${last.ts}
    `;
    alertBox.style.display = "block";
    document.body.style.background = "#ffe6e6";
    // alert("Test Debugc"+last.zscore.toFixed(2))
  } else {
    alertBox.style.display = "none";
    document.body.style.background = "white";
  }
}


// RELOAD ALL
async function reloadAll() {
  await loadPrice();
  await loadSpread();
  await loadCorrelation();
  await loadStats();
  await loadAlerts();
}

sym1Select.onchange = reloadAll;
sym2Select.onchange = reloadAll;
tfSelect.onchange = reloadAll;
zInput.onchange = loadAlerts;

/* Initial + auto refresh */
reloadAll();
setInterval(reloadAll, 5000);


function downloadPrice() {
  const sym = sym1Select.value;
  window.open(`/api/export/price?symbol=${sym}`, "_blank");
}

function downloadSpread() {
  const s1 = sym1Select.value;
  const s2 = sym2Select.value;
  window.open(`/api/export/spread?s1=${s1}&s2=${s2}`, "_blank");
}

function downloadCorrelation() {
  const s1 = sym1Select.value;
  const s2 = sym2Select.value;
  window.open(`/api/export/correlation?s1=${s1}&s2=${s2}`, "_blank");
}


// function downloadHourlySummary() {
//   const s1 = sym1Select.value;
//   const s2 = sym2Select.value;
//   window.open(
//     `/api/export/hourly_summary?s1=${s1}&s2=${s2}`,
//     "_blank"
//   );
// }

