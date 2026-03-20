// Content script - s injecte dans la page vinted.fr
// A acces aux vrais cookies de session

const POINTS_RELAIS = [
  { nom: "Locker Rain X Wash Bondoufle", uuid: "7d5b16ac-cc4c-4398-b07e-fbf8ac74c725", rate_uuid: "abe64f67-389f-4c2b-b270-39c733127c64" },
  { nom: "Rain x Wash", uuid: "56ce4063-e960-4f68-adcc-4c2d5610603e", rate_uuid: "99c3aec2-87a6-4435-b14b-68c376560184" },
  { nom: "Wash N Dry", uuid: "7fe02049-a4e6-47de-97bc-2131c78a112e", rate_uuid: "99c3aec2-87a6-4435-b14b-68c376560184" },
  { nom: "TLT Rapid Market (DPD)", uuid: "36455f4f-130a-45ed-bc43-f8f927aee30b", rate_uuid: "c16d2578-dd8c-4328-9b0c-55f0e8cfb084" },
  { nom: "TLT Rapid Market (Chronopost)", uuid: "491d0cc8-1c3e-4117-9833-1be724e5a2b2", rate_uuid: "c50f3c3e-90c1-4420-b46f-5b35f85c293b" },
  { nom: "SL Informatique", uuid: "fd42da4b-fcc6-48d1-bfc7-c7a1b08e32fa", rate_uuid: "c50f3c3e-90c1-4420-b46f-5b35f85c293b" },
  { nom: "Chronodrive", uuid: "3df26c07-3112-4c1c-b143-b08a7685587e", rate_uuid: "99c3aec2-87a6-4435-b14b-68c376560184" },
  { nom: "Tabac Le Pepere", uuid: "196024f1-1bdb-4a2a-8f86-4b1695da1cc1", rate_uuid: "99c3aec2-87a6-4435-b14b-68c376560184" },
  { nom: "Monoprix", uuid: "2fd1ea7e-9a1b-476c-8a9b-5db8fce4c77f", rate_uuid: "99c3aec2-87a6-4435-b14b-68c376560184" },
];

async function faireFetch(url, method, body) {
  const r = await fetch(url, {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify(body),
    credentials: "include",
  });
  const text = await r.text();
  return { status: r.status, text: text };
}

async function acheter(itemId) {
  console.log("[Vinted Auto] Achat item", itemId);

  // Etape 0 : build
  const r0 = await faireFetch(
    "https://www.vinted.fr/api/v2/purchases/checkout/build",
    "POST",
    { purchase_items: [{ id: parseInt(itemId), type: "transaction" }] }
  );
  console.log("[Vinted Auto] Etape 0 status:", r0.status, r0.text.substring(0, 200));
  if (r0.status !== 200 && r0.status !== 201) {
    return { succes: false, message: `Echec etape 0 (${r0.status}): ${r0.text.substring(0, 300)}` };
  }
  const data0 = JSON.parse(r0.text);
  const purchaseId = data0?.checkout?.id;
  if (!purchaseId) {
    return { succes: false, message: "Purchase ID introuvable" };
  }
  console.log("[Vinted Auto] Purchase ID:", purchaseId);

  // Etape 1 : PUT checkout
  const r1 = await faireFetch(
    `https://www.vinted.fr/api/v2/purchases/${purchaseId}/checkout`,
    "PUT",
    { components: { item_presentation_escrow_v2: {}, additional_service: {}, payment_method: {}, shipping_address: {}, shipping_pickup_options: {}, shipping_pickup_details: {} } }
  );
  console.log("[Vinted Auto] Etape 1 status:", r1.status);
  if (r1.status !== 200 && r1.status !== 201) {
    return { succes: false, message: `Echec etape 1 (${r1.status}): ${r1.text.substring(0, 300)}` };
  }
  const checkout1 = JSON.parse(r1.text)?.checkout || {};

  // Etape 2 : PATCH point relais
  const pickupTypes = checkout1?.components?.shipping_pickup_details?.pickup_types || {};
  const pickupOptions = pickupTypes?.pickup?.shipping_options || [];
  let selectedRateUuid, pointUuid, pointNom;

  if (pickupOptions.length === 0) {
    const pickupOption = checkout1?.components?.shipping_pickup_options || {};
    selectedRateUuid = pickupOption?.pickup_options?.pickup?.selected_rate_uuid;
    pointUuid = pickupOption?.pickup_options?.pickup?.shipping_point?.uuid;
    pointNom = "defaut";
  } else {
    const rateUuids = new Set(pickupOptions.map(o => o.rate_uuid));
    const point = POINTS_RELAIS.find(pt => rateUuids.has(pt.rate_uuid));
    if (point) {
      selectedRateUuid = point.rate_uuid;
      pointUuid = point.uuid;
      pointNom = point.nom;
    } else {
      selectedRateUuid = pickupOptions[0].rate_uuid;
      pointUuid = null;
      pointNom = "premier disponible";
    }
  }

  console.log("[Vinted Auto] Etape 2 point relais:", pointNom);
  const r2 = await faireFetch(
    `https://www.vinted.fr/api/v2/purchases/${purchaseId}/checkout`,
    "PATCH",
    { components: { shipping_pickup_options: { pickup_type: 2 }, shipping_pickup_details: { selected_rate_uuid: selectedRateUuid, shipping_point_uuid: pointUuid } } }
  );
  console.log("[Vinted Auto] Etape 2 status:", r2.status);
  if (r2.status !== 200 && r2.status !== 201) {
    return { succes: false, message: `Echec etape 2 (${r2.status}): ${r2.text.substring(0, 300)}` };
  }
  const checksum = JSON.parse(r2.text)?.checkout?.checksum;
  if (!checksum) {
    return { succes: false, message: "Checksum introuvable" };
  }

  // Etape 3 : paiement
  console.log("[Vinted Auto] Etape 3 : paiement");
  const r3 = await faireFetch(
    `https://www.vinted.fr/api/v2/purchases/${purchaseId}/payment`,
    "POST",
    { checksum: checksum, payment_options: { browser_info: { language: "fr-FR", color_depth: 32, java_enabled: false, screen_height: 956, screen_width: 1470, timezone_offset: -60 } } }
  );
  console.log("[Vinted Auto] Etape 3 status:", r3.status, r3.text.substring(0, 200));
  if (r3.status === 200 || r3.status === 201) {
    return { succes: true, message: `Achete via ${pointNom}` };
  }
  return { succes: false, message: `Echec paiement (${r3.status}): ${r3.text.substring(0, 300)}` };
}

// Polling : verifie toutes les secondes si achat_local.py a une demande
async function pollAchat() {
  try {
    const r = await fetch("http://localhost:4445/poll");
    if (r.status === 200) {
      const data = await r.json();
      if (data.item_id) {
        console.log("[Vinted Auto] Demande achat recue pour item", data.item_id);
        const result = await acheter(data.item_id);
        console.log("[Vinted Auto] Resultat:", result);
        await fetch("http://localhost:4445/result", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: data.item_id, ...result }),
        });
      }
    }
  } catch (e) {
    // serveur pas encore lance, on ignore
  }
  setTimeout(pollAchat, 1000);
}

console.log("[Vinted Auto] Content script demarre sur", window.location.href);
pollAchat();
