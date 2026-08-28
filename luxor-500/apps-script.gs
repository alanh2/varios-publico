/**
 * Backend del formulario de LUXOR 500 — PENDIENTE DE PRUEBAS.
 *
 * Cómo usarlo:
 *  1. Crear un Google Sheet nuevo. Extensiones > Apps Script. Pegar este archivo.
 *  2. Fila 1 del Sheet (opcional, se crea sola):
 *     fecha | nombre | apellido | email | telefono | pais | interes | mensaje | idioma | origen
 *  3. Implementar > Nueva implementación > Aplicación web.
 *     Ejecutar como: yo.  Quién tiene acceso: cualquier persona.
 *  4. Copiar la URL /exec y pegarla en SHEET_ENDPOINT dentro de index.html.
 */

const COLS = ['fecha', 'nombre', 'apellido', 'email', 'telefono', 'pais', 'interes', 'mensaje', 'idioma', 'origen'];

function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  const data = JSON.parse(e.postData.contents);

  if (sheet.getLastRow() === 0) sheet.appendRow(COLS);
  sheet.appendRow(COLS.map(c => data[c] || ''));

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}
