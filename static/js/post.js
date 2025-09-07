let currentLandmarkId = null; // 現在いるランドマークID
let landmarksGeoJSON = null;  // サーバから取得したランドマーク GeoJSON
let lastUserPos = null;       // 最新のユーザー位置

// ===========================
// ランドマークをサーバから取得
// ===========================
async function loadLandmarks() {
  try {
    const res = await fetch("/api/landmarks");
    const geojson = await res.json();

    if (!geojson || geojson.type !== "FeatureCollection") {
      console.error("Invalid landmarks data:", geojson);
      return;
    }

    landmarksGeoJSON = geojson;
    console.log("ランドマークデータを取得:", landmarksGeoJSON);

    // もし位置情報がすでにある場合は判定
    if (lastUserPos) {
      checkAndSetLandmark(lastUserPos.lon, lastUserPos.lat, lastUserPos.acc);
    }
  } catch (e) {
    console.error("ランドマーク取得失敗:", e);
  }
}

// ===========================
// Turf.js で現在地がランドマーク内か判定
// ===========================
function checkInsideAny(lon, lat, accuracyMeters = 30) {
  if (!landmarksGeoJSON?.features) return [];

  const pt = turf.point([lon, lat]);
  const bufferKm = Math.max(accuracyMeters, 30) / 1000;

  let hits = [];
  let nearest = null;
  let minDistance = Infinity;

  for (const f of landmarksGeoJSON.features) {
    let inside = false;
    try {
      inside = turf.booleanPointInPolygon(pt, f);
      if (!inside) {
        const buffered = turf.buffer(f, bufferKm, { units: "kilometers" });
        inside = turf.booleanPointInPolygon(pt, buffered);
      }
    } catch (_) {}

    if (inside) hits.push(f);

    // 現在地との距離計算（中心点との距離）
    const centroid = turf.centroid(f);
    const dist = turf.distance(pt, centroid, { units: "kilometers" });
    if (dist < minDistance) {
      minDistance = dist;
      nearest = f;
    }
  }

  if (nearest) {
    console.log("一番近いランドマーク:", nearest.properties?.name, "距離(km):", minDistance.toFixed(3));
  }

  console.log("判定結果（ヒットしたランドマーク）:", hits);
  return hits;
}

// ===========================
// 判定結果に応じて hidden input 更新
// ===========================
function updateCurrentLandmark(matches) {
  if (matches.length > 0) {
    const landmark = matches[0];
    currentLandmarkId = landmark.id;
    console.log("判定ヒットランドマーク:", landmark.properties?.name, "ID:", currentLandmarkId);

    // hidden input をフォームに作成
    const form = document.querySelector("form");
    if (!document.getElementById("landmark_id")) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "landmark_id";
      input.id = "landmark_id";
      form.appendChild(input);
    }
    document.getElementById("landmark_id").value = currentLandmarkId;
  } else {
    currentLandmarkId = null;
    const input = document.getElementById("landmark_id");
    if (input) input.value = "";
    console.log("ランドマーク内にいません");
  }
}

// ===========================
// 現在地を判定して hidden input に反映
// ===========================
function checkAndSetLandmark(lon, lat, accuracyMeters) {
  const hits = checkInsideAny(lon, lat, accuracyMeters);
  updateCurrentLandmark(hits);
}

// ===========================
// Geolocation 成功時
// ===========================
function onGeoSuccess(pos) {
  const { latitude, longitude, accuracy } = pos.coords;
  console.log("現在位置:", latitude, longitude, "精度:", accuracy);

  lastUserPos = { lat: latitude, lon: longitude, acc: accuracy };
  checkAndSetLandmark(longitude, latitude, accuracy);
}

// ===========================
// Geolocation エラー
// ===========================
function onGeoError(err) {
  console.warn("位置情報取得失敗:", err);
}

// ===========================
// ページロード時にランドマーク取得 & Geolocation 監視開始
// ===========================
document.addEventListener("DOMContentLoaded", async () => {
  await loadLandmarks();

  if (navigator.geolocation) {
    navigator.geolocation.watchPosition(onGeoSuccess, onGeoError, {
      enableHighAccuracy: true,
      maximumAge: 10_000,
      timeout: 10_000,
    });
  } else {
    console.warn("この端末は位置情報未対応です");
  }

  // フォーム送信制御
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    console.log("フォーム送信時 currentLandmarkId:", currentLandmarkId);
    if (!currentLandmarkId) {
      e.preventDefault();
      alert("現在いるランドマーク内でのみ投稿できます");
    }
  });
});
