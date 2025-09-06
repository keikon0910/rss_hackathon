// ====== Leaflet: 地図初期化 ======
const map = L.map("map").setView([35.68, 139.76], 13);
L.tileLayer("https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors, GDL.jp",
}).addTo(map);

// ====== 状態 ======
let landmarkLayer = null;
let landmarksGeoJSON = null;
let userMarker = null;
let accuracyCircle = null;
let lastUserPos = null;

// ====== ユーティリティ ======
function popupHTML(feature) {
  const name = feature.properties?.name ?? "ランドマーク";
  let html = `<strong>${name}</strong>`;

  // 作成日がある場合は表示
  if (feature.properties?.created_at) {
    const createdAt = new Date(feature.properties.created_at);
    html += `<br><small>作成日: ${createdAt.toLocaleString()}</small>`;
  }

  return html;
}

// ====== ランドマーククリック時の処理 ======
function onLandmarkClick(feature) {
  console.log("ランドマークがクリックされました:", feature); // ← デバッグ用ログ

  const name = feature.properties?.name ?? "ランドマーク";
  const createdAtStr = feature.properties?.created_at ?? null;

  let createdAtText = "作成日情報なし";
  if (createdAtStr) {
    const createdAt = new Date(createdAtStr);
    createdAtText = createdAt.toLocaleString();
  }

  const infoP = document.getElementById("landmark-info");
  if (infoP) {
    infoP.textContent = `${name}（作成日: ${createdAtText}）`;
    console.log("情報を <p> に表示:", infoP.textContent); // ← デバッグ用ログ
  } else {
    console.warn("<p> 要素が見つかりません");
  }

  // 下のパネルも表示する場合
  const panel = document.getElementById("landmark-panel");
  if (panel) {
    panel.classList.remove("hidden");
    console.log("ランドマークパネルを表示");
  }
}

// ====== landmarkLayer 作成時にクリックイベント登録 ======
if (landmarkLayer) {
  landmarkLayer.eachLayer((layer) => {
    layer.on("click", () => onLandmarkClick(layer.feature));
  });
} else {
  console.warn("ランドマークレイヤーが存在しません");
}



function updateUserMarker(lat, lon, acc) {
  const latlng = [lat, lon];
  if (!userMarker) {
    userMarker = L.marker(latlng).addTo(map).bindPopup("あなたの位置");
  } else {
    userMarker.setLatLng(latlng);
  }
  if (!accuracyCircle) {
    accuracyCircle = L.circle(latlng, { radius: acc }).addTo(map);
  } else {
    accuracyCircle.setLatLng(latlng);
    accuracyCircle.setRadius(acc);
  }
}

// CTA（青いボタン or メッセージ）を切り替え
function setCTA(matches) {
  const linkEl = document.getElementById("cta-link");
  const nameEl = document.getElementById("cta-name");
  const msgEl = document.getElementById("cta-msg");

  if (!linkEl || !nameEl || !msgEl) return;

  if (matches.length > 0) {
    const f = matches[0];
    const name = f.properties?.name ?? "ランドマーク";
    nameEl.textContent = name;

    // Flask 側の投稿ページへ。landmark_id はクエリに追加
    linkEl.href = `/photograph/post?landmark_id=${f.id}`;
    linkEl.style.display = "inline-block";
    msgEl.style.display = "none";
  } else {
    linkEl.style.display = "none";
    msgEl.style.display = "inline";
  }
}

// 点がランドマーク内か判定
function checkInsideAny(lon, lat, accuracyMeters = 30) {
  if (!landmarksGeoJSON || !landmarksGeoJSON.features) return [];
  const pt = turf.point([lon, lat]);
  const bufferKm = Math.max(accuracyMeters, 30) / 1000;

  console.log("ユーザー位置:", [lon, lat]); // ← ここで現在位置を出力

  const hits = [];
  for (const f of landmarksGeoJSON.features) {
    let inside = false;
    try {
      inside = turf.booleanPointInPolygon(pt, f); // ポリゴン内判定
      if (!inside) {
        const buffered = turf.buffer(f, bufferKm, { units: "kilometers" });
        inside = turf.booleanPointInPolygon(pt, buffered); // 精度分の余裕も判定
      }
    } catch (_) {}

    console.log(`ランドマーク "${f.properties?.name}" 内判定:`, inside); // ← 判定結果を出力

    if (inside) hits.push(f);
  }

  console.log("判定結果（ヒットしたランドマーク）:", hits); // ← 最終結果を出力
  return hits; // ランドマーク内なら配列に入れる
}


// ====== ランドマークを読み込んで描画 ======
async function loadLandmarks() {
  try {
    const res = await fetch("/api/landmarks");
    const geojson = await res.json();

    // ★ここでブラウザのコンソールに表示
    console.log("取得したランドマークデータ:", geojson);

    if (!geojson || geojson.type !== "FeatureCollection") {
      console.error("Invalid /api/landmarks payload:", geojson);
      return;
    }

    landmarksGeoJSON = geojson;

    if (landmarkLayer) map.removeLayer(landmarkLayer);
    landmarkLayer = L.geoJSON(geojson, {
      style: { color: "#2563eb", weight: 2, fillOpacity: 0.15 },
      onEachFeature: (f, layer) => layer.bindPopup(popupHTML(f)),
    }).addTo(map);

    const b = landmarkLayer.getBounds();
    if (b.isValid()) map.fitBounds(b.pad(0.2));

    if (lastUserPos) {
      const { lat, lon, acc } = lastUserPos;
      setCTA(checkInsideAny(lon, lat, acc));
    }
  } catch (e) {
    console.error("Failed to load landmarks:", e);
  }
}

loadLandmarks();

// ====== Geolocation ======
function onGeoSuccess(pos) {
  const { latitude, longitude, accuracy } = pos.coords;
  updateUserMarker(latitude, longitude, accuracy);
  lastUserPos = { lat: latitude, lon: longitude, acc: accuracy };
  setCTA(checkInsideAny(longitude, latitude, accuracy));
}

function onGeoError(err) {
  console.warn("Geolocation error:", err);
  const msgEl = document.getElementById("cta-msg");
  if (msgEl) msgEl.textContent = `位置情報が取得できません（${err.message}）`;
}

if (navigator.geolocation) {
  navigator.geolocation.watchPosition(onGeoSuccess, onGeoError, {
    enableHighAccuracy: true,
    maximumAge: 10_000,
    timeout: 10_000,
  });
} else {
  const msgEl = document.getElementById("cta-msg");
  if (msgEl) msgEl.textContent = "この端末は位置情報に未対応です";
}


// ====== landmarkLayer クリック時の情報表示 ======
function setupLandmarkClickEvents() {
  if (!landmarkLayer) {
    console.warn("ランドマークレイヤーが存在しません");
    return;
  }

  landmarkLayer.eachLayer((layer) => {
    layer.on("click", () => {
      const f = layer.feature;
      console.log("ランドマークがクリックされました:", f);

      const name = f.properties?.name ?? "ランドマーク";
      const createdAtStr = f.properties?.created_at ?? null;
      const createdAtText = createdAtStr ? new Date(createdAtStr).toLocaleString() : "作成日情報なし";

      // <h2 id="lmName"> にランドマーク名を表示
      const lmName = document.getElementById("lmName");
      if (lmName) {
        lmName.textContent = name;
        console.log("<h2> に表示:", lmName.textContent);
      }

      // <p id="landmark-info"> に作成日を表示
      const infoP = document.getElementById("landmark-info");
      if (infoP) {
        infoP.textContent = `作成日: ${createdAtText}`;
        console.log("<p> に表示:", infoP.textContent);
      }

      // 投稿ボタンは非表示または無効化（表示させない）
      const postLink = document.getElementById("postLink");
      if (postLink) {
        postLink.style.display = "none"; // 完全に非表示にする
        // もし表示したいけど遷移させたくない場合:
        // postLink.href = "#";
        // postLink.onclick = (e) => e.preventDefault();
      }

      // 下のパネルを表示
      const panel = document.getElementById("landmark-panel");
      if (panel) panel.classList.remove("hidden");
    });
  });
}



// landmarks を読み込んだ後に呼び出す
loadLandmarks().then(() => {
  setupLandmarkClickEvents();
});
