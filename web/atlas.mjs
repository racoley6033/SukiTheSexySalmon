/** Exact 3×2 raster-atlas crops; exported so the same code can be used in other apps. */
export const EXPRESSIONS = ['happy', 'wink', 'flirty', 'excited', 'sassy', 'surprised'];
export function sourceRect(width, height, expression) {
  const index = EXPRESSIONS.indexOf(expression);
  if (index < 0) throw new Error(`Unknown expression: ${expression}`);
  if (width % 3 || height % 2 || width <= 0 || height <= 0) {
    throw new Error('The expression atlas must divide evenly into 3 columns and 2 rows.');
  }
  const w = width / 3, h = height / 2;
  return {x: (index % 3) * w, y: Math.floor(index / 3) * h, width: w, height: h};
}
export function drawExpression(image, expression, canvas = document.createElement('canvas')) {
  const rect = sourceRect(image.naturalWidth, image.naturalHeight, expression);
  canvas.width = rect.width; canvas.height = rect.height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Canvas is unavailable in this browser.');
  context.drawImage(image, rect.x, rect.y, rect.width, rect.height, 0, 0, rect.width, rect.height);
  return canvas;
}
export async function downloadExpression(canvas, expression) {
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
  if (!blob) throw new Error('Could not encode the expression PNG.');
  const url = URL.createObjectURL(blob), anchor = document.createElement('a');
  anchor.href = url; anchor.download = `suki-${expression}-illustrated.png`;
  anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export async function mountAtlas(container) {
  const image = new Image(); image.src = 'assets/artwork/suki-expressions-atlas.png';
  await image.decode();
  for (const expression of EXPRESSIONS) {
    const article = document.createElement('article');
    const canvas = drawExpression(image, expression); canvas.style.width = '100%';
    canvas.setAttribute('role', 'img'); canvas.setAttribute('aria-label', `Illustrated Suki ${expression}`);
    const heading = document.createElement('h3'); heading.textContent = expression;
    const button = document.createElement('button'); button.textContent = 'Download transparent PNG';
    button.addEventListener('click', () => downloadExpression(canvas, expression).catch(error => {
      button.textContent = error.message;
    }));
    article.append(canvas, heading, button); container.append(article);
  }
}
